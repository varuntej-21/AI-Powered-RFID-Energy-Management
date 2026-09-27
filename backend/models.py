# backend/models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import os

Base = declarative_base()

# -------- Database Setup --------
DATA_DIR = os.path.join(os.path.dirname(__file__), "../data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "app.db")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

# -------- Models --------
class User(Base):
    __tablename__ = "users"
    uid = Column(String, primary_key=True)             # RFID UID
    name = Column(String, default="Unknown")
    quota_kwh = Column(Float, default=0.0)
    account_type = Column(String, default="savings")
    balance = Column(Float, default=1000.0)
    pin_hash = Column(String, default="")              # hashed PIN

class SessionLog(Base):
    __tablename__ = "session_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String)
    start_ts = Column(DateTime, default=datetime.utcnow)
    end_ts = Column(DateTime, nullable=True)
    energy_kwh = Column(Float, default=0.0)
    cost_rs = Column(Float, default=0.0)

class DeviceState(Base):
    __tablename__ = "device_state"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String, nullable=True)
    relay_on = Column(Boolean, default=False)
    power_w_assumed = Column(Float, default=0.0)
    last_seen = Column(DateTime, default=datetime.utcnow)

# -------- Init function --------
def init_db():
    Base.metadata.create_all(engine)
