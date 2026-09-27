# dashboard/app.py — PIN gate + no static balance + fast hide after removal
import requests, pandas as pd, streamlit as st
from datetime import datetime

BACKEND = "http://10.30.109.26:8000"  # <- your backend IP

st.set_page_config(page_title="ATM OF HYD", page_icon="🏧", layout="wide")
st.title("ATM OF HYD")
st.markdown("**Welcome — please place your card on the reader.**")

# --- Sidebar ---
with st.sidebar:
    st.header("Admin / Controls")
    if st.button("Seed demo users", key="seed_button"):
        try:
            requests.post(f"{BACKEND}/seed", timeout=3)
            st.success("✅ Seeded sample users (PIN 2003).")
        except Exception:
            st.error("❌ Backend unreachable.")
    REFRESH = st.slider("Refresh (sec)", 1, 3, 1, key="refresh_slider")

# Auto-refresh page
st.write(
    f"<script>setTimeout(() => window.parent.location.reload(), {REFRESH*1000});</script>",
    unsafe_allow_html=True,
)

def safe_get(url, default=None, timeout=3):
    try:
        r = requests.get(url, timeout=timeout)
        if r.ok: return r.json()
    except Exception:
        pass
    return default

def safe_post(url, payload=None, timeout=3):
    try:
        r = requests.post(url, json=payload or {}, timeout=timeout)
        return r.json() if r.ok else {"error": r.status_code}
    except Exception as e:
        return {"error": str(e)}

status_ph, menu_ph, log_ph = st.empty(), st.empty(), st.empty()

live = safe_get(f"{BACKEND}/live", default={})
if not live:
    status_ph.error("❌ Backend not reachable.")
else:
    device = live.get("device", {}) or {}
    user = live.get("user", {}) or {}
    presence = device.get("presence", False)
    uid_now = device.get("uid")

    # reset PIN gate if no presence or UID changed
    prev_uid = st.session_state.get("pin_uid")
    if not presence or (prev_uid and prev_uid != uid_now):
        st.session_state["pin_ok"] = False
        st.session_state["pin_uid"] = uid_now

    if presence:
        uid = uid_now or "Unknown"
        name = (user or {}).get("name") or uid
        status_ph.success(f"💳 Card inserted: **{name}** (UID: {uid}). Session active.")
        ks = f"_{uid}"

        with menu_ph.container():
            acct_type = (user or {}).get("account_type", "unknown").title()
            st.subheader(f"Welcome, {name}")
            st.markdown(f"**Account type:** {acct_type}")

            # PIN gate
            pin_ok = st.session_state.get("pin_ok", False)
            if not pin_ok:
                st.info("🔐 Enter your PIN to continue.")
                pin_val = st.text_input("Enter PIN", type="password", max_chars=6, key=f"pin_input{ks}")
                if st.button("Verify PIN", key=f"verify_pin{ks}"):
                    resp = safe_post(f"{BACKEND}/pin/verify", {"uid": uid, "pin": pin_val})
                    if resp.get("ok"):
                        st.session_state["pin_ok"] = True
                        st.session_state["pin_uid"] = uid
                        st.success("✅ PIN verified.")
                        st.write("<script>setTimeout(()=>window.parent.location.reload(), 500);</script>", unsafe_allow_html=True)
                    else:
                        st.error("❌ Incorrect PIN.")
                st.stop()  # don't render actions until PIN ok

            st.markdown("Choose an option:")
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1])

            if c1.button("Balance Enquiry", key=f"balance_enquiry{ks}"):
                j = safe_get(f"{BACKEND}/balance/{uid}", default={})
                st.info(f"💰 Balance: ₹ {j.get('balance', 0.0):.2f}")

            amt = c2.number_input("Withdraw amount (₹)", min_value=0.0, step=100.0, key=f"wd_amt{ks}")
            if c2.button("Withdraw Now", key=f"withdraw_now{ks}"):
                if amt <= 0:
                    st.warning("Enter an amount > 0")
                else:
                    res = safe_post(f"{BACKEND}/withdraw", {"uid": uid, "amount": float(amt)})
                    if "balance" in res:
                        st.success(f"✅ Withdrawal successful. New balance: ₹ {res['balance']:.2f}")
                        st.write("<script>setTimeout(()=>window.parent.location.reload(), 800);</script>", unsafe_allow_html=True)
                    else:
                        st.error(f"⚠️ Withdrawal failed: {res}")

            if c3.button("End Session", key=f"end_session{ks}"):
                safe_post(f"{BACKEND}/session/stop", {"uid": uid})
                st.session_state["pin_ok"] = False
                st.success("🟢 Session ended. Remove card.")
                st.write("<script>setTimeout(()=>window.parent.location.reload(), 500);</script>", unsafe_allow_html=True)

            if c4.button("Cancel (Keep Card)", key=f"cancel{ks}"):
                st.info("Session continues; remove card to end.")

        # Logs
        sessions = safe_get(f"{BACKEND}/sessions", default=[])
        if isinstance(sessions, dict):
            sessions = sessions.get("sessions", sessions.get("active_sessions", [])) or []
        if sessions and isinstance(sessions, list):
            df = pd.DataFrame(sessions)
            if not df.empty:
                if "start_ts" in df.columns:
                    df["start_ts"] = pd.to_datetime(df["start_ts"], errors="coerce")
                log_ph.dataframe(df.tail(10), use_container_width=True)
            else:
                log_ph.caption("No sessions yet.")
        else:
            log_ph.caption("No sessions data available.")
    else:
        status_ph.info("🟡 No card detected. Please place your card on the reader.")
        menu_ph.empty()
        log_ph.empty()
        st.session_state["pin_ok"] = False
        st.session_state["pin_uid"] = None
