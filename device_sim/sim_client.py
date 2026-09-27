import time, requests, random

BASE = "http://127.0.0.1:8000"
UID = "AB12CD34"
POWER_W = 100.0

def post(path, payload):
    r = requests.post(BASE + path, json=payload, timeout=5)
    return r.json()

def simulate_session(seconds=20):
    print("START session")
    print(post("/session/start", {"uid": UID}))
    t0 = time.time()
    while time.time() - t0 < seconds:
        j = {"uid": UID, "relay_on": True, "power_w": POWER_W + random.uniform(-3,3)}
        post("/telemetry", j)
        time.sleep(2.0)
    print("STOP session")
    print(post("/session/stop", {"uid": UID}))

if __name__ == "__main__":
    simulate_session(18)
    time.sleep(5)
    simulate_session(26)
