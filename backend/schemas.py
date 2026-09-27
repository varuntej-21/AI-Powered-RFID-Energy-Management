from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class StartReq(BaseModel):
    uid: str

class StopReq(BaseModel):
    uid: str

class Telemetry(BaseModel):
    uid: str
    relay_on: bool
    power_w: float

class UserIn(BaseModel):
    uid: str
    name: str
