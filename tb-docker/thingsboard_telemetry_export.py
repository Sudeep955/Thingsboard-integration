import requests
import os
import csv
import time
from datetime import datetime, timedelta

# === CONFIG ===
BASE_URL = "http://localhost:8080"
USERNAME = "tenant@thingsboard.org"   # 👈 Your ThingsBoard username
PASSWORD = "tenant"                   # 👈 Your ThingsBoard password

CSV_DIR = "exported_telemetry_data"
os.makedirs(CSV_DIR, exist_ok=True)

# === DEVICE LIST ===
DEVICES = {
    "Battery": "099ce090-2266-11f0-8b02-17f9d5168c83",
    "Temperature": "f9bc8bd0-2265-11f0-8b02-17f9d5168c83",
    "Irradiance": "eb8ea200-2265-11f0-8b02-17f9d5168c83",
    "Power": "dda00b20-2265-11f0-8b02-17f9d5168c83",
    "Current": "cdef03c0-2265-11f0-8b02-17f9d5168c83",
    "Voltage": "be8da300-2265-11f0-8b02-17f9d5168c83",
    "Panel_tilt": "23407200-2266-11f0-8b02-17f9d5168c83",
}

# === TIME RANGE ===
end_time = int(time.time() * 1000)  # Now
start_time = int((datetime.now() - timedelta(days=3)).timestamp() * 1000)  # 3 days ago

# === AUTH FUNCTION ===
def get_jwt_token():
    login_url = f"{BASE_URL}/api/auth/login"
    credentials = {"username": USERNAME, "password": PASSWORD}
    res = requests.post(login_url, json=credentials)
    res.raise_for_status()
    token = res.json()["token"]
    return f"Bearer {token}"

# === FETCH FUNCTION ===
def fetch_and_save(device_name, device_id, jwt_token):
    key = device_name
    url = f"{BASE_URL}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
    params = {
        "keys": key,
        "startTs": start_time,
        "endTs": end_time,
        "interval": 60000,
        "limit": 10000,
        "agg": "NONE"
    }
    headers = {
        "Content-Type": "application/json",
        "X-Authorization": jwt_token
    }

    try:
        print(f"📡 Fetching {key} telemetry...")
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
        data = res.json()

        records = data.get(key, [])
        if not records:
            print(f"⚠ No data for {device_name}")
            return

        filepath = os.path.join(CSV_DIR, f"{device_name}.csv")
        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["timestamp", key])
            writer.writeheader()
            for row in records:
                ts = datetime.fromtimestamp(row["ts"] / 1000.0).isoformat()
                writer.writerow({"timestamp": ts, key: row["value"]})
        print(f"✅ Saved to {filepath}")

    except Exception as e:
        print(f"❌ Error for {device_name}: {e}")

# === MAIN ===
def main():
    jwt_token = get_jwt_token()   # 👈 Get fresh token here
    for name, device_id in DEVICES.items():
        fetch_and_save(name, device_id, jwt_token)

if __name__ == "__main__":
    main()
