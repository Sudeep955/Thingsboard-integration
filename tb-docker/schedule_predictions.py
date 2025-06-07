import pandas as pd
import joblib
import json
import paho.mqtt.client as mqtt
import schedule
import time

# MQTT Config
BROKER = "localhost"
ACCESS_TOKEN = "oR4VKDeTFtHBrH0UAPiU"  # Replace with your Power_Predicted token

# Features used by the model
features = ['battery', 'current', 'irradiance', 'panel_tilt', 'temperature', 'voltage']

# Load model once
model = joblib.load("power_prediction_rf_model.pkl")



def predict_and_send():
    try:
        # Load latest telemetry data
        df = pd.read_csv("merged_telemetry_data.csv")
        df[features] = df[features].apply(pd.to_numeric, errors='coerce')
        df.dropna(inplace=True)

        if df.empty:
            print("⚠ No valid data available.")
            return

        latest = df[features].tail(1)
        predicted_power = model.predict(latest)[0]
        payload = json.dumps({"predicted_power": float(round(predicted_power, 2))})


        # Send to ThingsBoard
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.username_pw_set(ACCESS_TOKEN)
        client.connect(BROKER, 1883, 60)
        client.publish("v1/devices/me/telemetry", payload)
        client.disconnect()

        print(f"✅ Sent: {payload}")

    except Exception as e:
        print(f"❌ Error: {e}")

# Schedule every 5 minutes
schedule.every(5).minutes.do(predict_and_send)

print("⏳ Scheduler started. Predicting and sending every 5 minutes...")

# Run forever
while True:
    schedule.run_pending()
    time.sleep(1)