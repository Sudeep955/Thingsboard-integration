from flask import Flask, jsonify
import requests
import time

app = Flask(__name__)

# Config
THINGSBOARD_URL = "http://localhost:8080"

USERNAME = "tenant@thingsboard.org"
PASSWORD = "tenant"

# Time window for history (last 30 days)
END_TS = int(time.time() * 1000)            # now, in milliseconds
START_TS = END_TS - (30 * 24 * 60 * 60 * 1000)  # 30 days ago

def get_token():
    url = f"{THINGSBOARD_URL}/api/auth/login"
    resp = requests.post(url, json={"username": USERNAME, "password": PASSWORD})
    resp.raise_for_status()
    return resp.json().get("token")

def get_all_devices(token):


































































    
    url = f"{THINGSBOARD_URL}/api/tenant/devices?pageSize=100&page=0"
    headers = {"X-Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json().get("data", [])

def get_device_keys(token, device_id):
    """Get all telemetry keys for device (latest values endpoint to get keys)."""
    url = f"{THINGSBOARD_URL}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
    headers = {"X-Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    data = resp.json()
    return list(data.keys())

def get_telemetry_history(token, device_id, key, start_ts, end_ts):
    url = f"{THINGSBOARD_URL}/api/plugins/telemetry/DEVICE/{device_id}/values/timeseries"
    headers = {"X-Authorization": f"Bearer {token}"}
    params = {
        "keys": key,
        "startTs": start_ts,
        "endTs": end_ts,
        "limit": 1000,   # max records to fetch per call
        "order": "ASC"
    }
    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json().get(key, [])

@app.route("/")
def home():
    return "✅ Use /api to get all telemetry history from all devices (last 30 days)."

@app.route("/api")
def api():
    try:
        token = get_token()
        devices = get_all_devices(token)
        all_history = {}

        for device in devices:
            device_name = device.get("name")
            device_id = device.get("id", {}).get("id")
            if not device_id:
                continue
            
            keys = get_device_keys(token, device_id)
            device_history = {}

            for key in keys:
                history = get_telemetry_history(token, device_id, key, START_TS, END_TS)
                device_history[key] = history
            
            all_history[device_name] = device_history

        return jsonify(all_history)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
