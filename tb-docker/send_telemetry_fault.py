import pandas as pd
import joblib
import requests
import time
from sklearn.metrics import mean_absolute_error

# === Configuration ===
ACCESS_TOKEN = 'oR4VKDeTFtHBrH0UAPiU'  # Power_Predicted device token
POST_URL = f'http://localhost:8080/api/v1/{ACCESS_TOKEN}/telemetry'
MODEL_PATH = 'C:/Users/Hp/OneDrive/Desktop/tb-docker/power_prediction_rf_model.pkl'
DATA_PATH = 'C:/Users/Hp/OneDrive/Desktop/tb-docker/merged_telemetry_data.csv'

FEATURES = ['battery', 'current', 'irradiance', 'panel_tilt', 'temperature', 'voltage']

# === Load model and data ===
model = joblib.load(MODEL_PATH)

try:
    df = pd.read_csv(DATA_PATH)
    print("✅ Data loaded successfully.")
    print(df.head())
except Exception as e:
    print(f"❌ Error loading data: {e}")
    exit()

# === Clean the data ===
df = df.dropna(subset=['power'])  # Drop rows where 'power' is NaN
df[FEATURES] = df[FEATURES].fillna(method='ffill')  # Forward fill
df[FEATURES] = df[FEATURES].fillna(method='bfill')  # Backward fill

# === Calculate dynamic threshold ===
y_true = df['power']
y_pred = model.predict(df[FEATURES])
mae = mean_absolute_error(y_true, y_pred)
threshold = 2 * mae  # Adjust multiplier if needed

print(f"📈 Mean Absolute Error (MAE): {mae:.2f}")
print(f"⚙️ Dynamic Fault Threshold set to: {threshold:.2f}")

# === Iterate and send telemetry ===
for i, row in df.iterrows():
    input_data = pd.DataFrame([row[FEATURES].values], columns=FEATURES)

    if input_data.isnull().values.any():
        print(f"❌ Skipping row {i} due to NaN values in the features.")
        continue

    predicted_power = float(model.predict(input_data)[0])
    actual_power = row['power']
    error = abs(actual_power - predicted_power)
    fault = int(error > threshold)

    telemetry = {
        "predicted_power": predicted_power,
        "actual_power": actual_power,
        "fault": fault  # <-- dynamically set
    }

    try:
        response = requests.post(POST_URL, json=telemetry)
        print(f"✅ Sent: {telemetry} | Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending telemetry: {e}")

    time.sleep(2)
