import pandas as pd
import joblib
import json
import paho.mqtt.client as mqtt

# Load the trained model
model = joblib.load("power_prediction_rf_model.pkl")

# Read the most recent telemetry
df = pd.read_csv("merged_telemetry_data.csv")

# Define features
features = ['battery', 'current', 'irradiance', 'panel_tilt', 'temperature', 'voltage']

# Convert to numeric and drop rows with missing values
df[features] = df[features].apply(pd.to_numeric, errors='coerce')
df.dropna(inplace=True)

# Use the latest row for prediction
latest = df[features].tail(1)
predicted_power = model.predict(latest)[0]

# MQTT Configuration
BROKER = "localhost"  # If ThingsBoard is running locally
ACCESS_TOKEN = "NaR66eqeirgKmzZCTwo1"  # <-- Replace with your Power_Predicted device token

# Prepare MQTT client and send prediction
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(ACCESS_TOKEN)
client.connect(BROKER, 1883, 60)

# Send payload
payload = json.dumps({"predicted_power": round(predicted_power, 2)})
client.publish("v1/devices/me/telemetry", payload)

print(f"✅ Sent predicted power to ThingsBoard: {payload}")
client.disconnect()