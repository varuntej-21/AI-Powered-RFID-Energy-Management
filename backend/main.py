# backend/main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import hashlib

from .models import init_db, SessionLocal, User, SessionLog, DeviceState
from .schemas import StartReq, StopReq, Telemetry, UserIn

TARIFF_RS_PER_KWH = 8.0
TELEMETRY_PERIOD_S = 2.0
PRESENCE_TIMEOUT_S = 3  # UI clears quickly after card removal

app = FastAPI(title="RFID ATM Backend", version="1.3")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
init_db()

# ---------- helpers ----------
def hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

def get_active_session(db, uid: str) -> Optional[SessionLog]:
    return db.query(SessionLog).filter(SessionLog.uid == uid, SessionLog.end_ts == None).first()

def get_state_row(db) -> DeviceState:
    st = db.query(DeviceState).order_by(DeviceState.id.desc()).first()
    if not st:
        st = DeviceState()
        db.add(st); db.commit(); db.refresh(st)
    return st

# ---------- local schemas ----------
class PresenceReq(BaseModel):
    uid: str

class PinReq(BaseModel):
    uid: str
    pin: str

class WithdrawReq(BaseModel):
    uid: str
    amount: float

# ---------- endpoints ----------
@app.get("/health")
def health():
    return {"ok": True, "ts": datetime.utcnow().isoformat()}

@app.post("/seed")
def seed():
    with SessionLocal() as db:
        for uid, name, acct, bal, pin in [
            ("AB12CD34", "Varun", "savings", 5000.0, "2003"),
            ("DEADBEEF", "TestUser", "current", 2500.0, "2003"),
        ]:
            u = db.get(User, uid)
            if not u:
                db.add(User(uid=uid, name=name, account_type=acct, balance=bal, pin_hash=hash_pin(pin)))
            else:
                if not getattr(u, "account_type", None):
                    u.account_type = acct
                if getattr(u, "balance", None) is None:
                    u.balance = bal
                if not getattr(u, "pin_hash", ""):
                    u.pin_hash = hash_pin(pin)
        db.commit()
    return {"ok": True}

@app.post("/users")
def upsert_user(u: UserIn):
    with SessionLocal() as db:
        row = db.get(User, u.uid)
        if row:
            row.name = u.name
        else:
            db.add(User(uid=u.uid, name=u.name, account_type="savings", balance=1000.0, pin_hash=hash_pin("2003")))
        db.commit()
        return {"ok": True}

@app.post("/pin/verify")
def verify_pin(p: PinReq):
    with SessionLocal() as db:
        u = db.get(User, p.uid)
        if not u:
            raise HTTPException(status_code=404, detail="User not found")
        if not u.pin_hash:
            u.pin_hash = hash_pin("2003"); db.commit()
        return {"ok": (u.pin_hash == hash_pin(p.pin))}

@app.post("/presence")
def presence(p: PresenceReq):
    try:
        with SessionLocal() as db:
            # ensure user exists
            user = db.get(User, p.uid)
            if not user:
                user = User(uid=p.uid, name=p.uid, account_type="savings", balance=1000.0, pin_hash=hash_pin("2003"))
                db.add(user); db.commit()

            # device heartbeat
            st = get_state_row(db)
            st.uid = p.uid
            st.relay_on = True
            st.last_seen = datetime.utcnow()
            db.commit()

            # open session if not active
            s = get_active_session(db, p.uid)
            if not s:
                s = SessionLog(uid=p.uid)
                db.add(s); db.commit()
                return {"status": "session-started", "session_id": s.id}
            return {"status": "presence-ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"presence_failed: {e}")

@app.post("/session/stop")
def stop_session(payload: StopReq):
    with SessionLocal() as db:
        s = get_active_session(db, payload.uid)
        if not s:
            return {"status": "no-active-session"}
        s.end_ts = datetime.utcnow()
        s.cost_rs = s.energy_kwh * TARIFF_RS_PER_KWH
        st = get_state_row(db)
        st.uid = payload.uid
        st.relay_on = False
        st.last_seen = datetime.utcnow()
        db.commit()
        return {"status": "stopped", "session_id": s.id, "kwh": s.energy_kwh, "rs": s.cost_rs}

@app.post("/telemetry")
def telemetry(t: Telemetry):
    with SessionLocal() as db:
        st = get_state_row(db)
        st.uid = t.uid or st.uid
        st.relay_on = bool(t.relay_on)
        st.power_w_assumed = float(t.power_w)
        st.last_seen = datetime.utcnow()
        s = get_active_session(db, st.uid)
        if s and st.relay_on:
            dt_h = TELEMETRY_PERIOD_S / 3600.0
            s.energy_kwh += (st.power_w_assumed * dt_h) / 1000.0
            s.cost_rs = s.energy_kwh * TARIFF_RS_PER_KWH
        db.commit()
        return {"ok": True}

@app.get("/live")
def live():
    with SessionLocal() as db:
        st = get_state_row(db)
        last = st.last_seen or datetime.utcnow()
        # Presence purely time-based for fast drop-out
        presence_ok = (datetime.utcnow() - last).total_seconds() <= PRESENCE_TIMEOUT_S

        # Auto-stop any dangling active session as soon as presence is gone
        if not presence_ok:
            active = db.query(SessionLog).filter(SessionLog.end_ts == None).all()
            if active:
                for s in active:
                    s.end_ts = datetime.utcnow()
                    s.cost_rs = s.energy_kwh * TARIFF_RS_PER_KWH
                st.relay_on = False
                db.commit()

        active_now = db.query(SessionLog).filter(SessionLog.end_ts == None).all()
        total_kw = (st.power_w_assumed / 1000.0) if st.relay_on else 0.0
        user = db.get(User, st.uid) if (presence_ok and st.uid) else None

        return {
            "device": {
                "uid": st.uid, "relay_on": bool(st.relay_on),
                "power_w": float(st.power_w_assumed), "presence": presence_ok,
                "last_seen": last.isoformat(),
            },
            "user": ({
                "uid": user.uid, "name": user.name,
                "account_type": user.account_type, "balance": user.balance
            } if user else None),
            "active_sessions": [
                {"id": s.id, "uid": s.uid, "start_ts": s.start_ts,
                 "end_ts": s.end_ts, "energy_kwh": round(s.energy_kwh, 6),
                 "cost_rs": round(s.cost_rs, 2)}
                for s in active_now
            ],
            "total_kw": round(total_kw, 3),
            "tariff": TARIFF_RS_PER_KWH,
        }

@app.post("/withdraw")
def withdraw(w: WithdrawReq):
    with SessionLocal() as db:
        user = db.get(User, w.uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if w.amount <= 0:
            raise HTTPException(status_code=400, detail="Invalid amount")
        if user.balance < w.amount:
            return {"status": "insufficient", "balance": user.balance}
        user.balance -= w.amount
        db.commit()
        return {"status": "ok", "balance": user.balance}

@app.get("/balance/{uid}")
def balance(uid: str):
    with SessionLocal() as db:
        user = db.get(User, uid)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"uid": user.uid, "name": user.name, "account_type": user.account_type, "balance": user.balance}
