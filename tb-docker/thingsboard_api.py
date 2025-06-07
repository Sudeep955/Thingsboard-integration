from flask import Flask, jsonify
import requests

app = Flask(__name__)

# Config - Replace below values
THINGSBOARD_URL = "http://<your-PC-IP>:8080"  # e.g., http://192.168.1.10:8080
USERNAME = "tenant@thingsboard.org"
PASSWORD = "tenant"
DEVICE_ID = "<your-device-id>"  # Paste your actual device ID here

def get_token():
    url = f"{THINGSBOARD_URL}/api/auth/login"
    resp = requests.post(url, json={"username": USERNAME, "password": PASSWORD})
    resp.raise_for_status()
    return resp.json().get("token")

@app.route("/public-telemetry")
def public_telemetry():
    try:
        token = get_token()
        headers = {"X-Authorization": f"Bearer {token}"}
        keys = "temperature,humidity"  # change keys as per your device

        url = f"{THINGSBOARD_URL}/api/plugins/telemetry/DEVICE/{DEVICE_ID}/values/timeseries"
        resp = requests.get(url, headers=headers, params={"keys": keys})
        resp.raise_for_status()
        return jsonify(resp.json())

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
