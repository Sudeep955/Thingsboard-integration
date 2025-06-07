import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# === Load and Clean the Data ===
df = pd.read_csv("merged_telemetry_data.csv")

# Define features and target
features = ['battery', 'current', 'irradiance', 'panel_tilt', 'temperature', 'voltage']
target = 'power'

# Keep only the relevant columns
df = df[['timestamp'] + features + [target]]

# Convert feature columns to numeric
df[features + [target]] = df[features + [target]].apply(pd.to_numeric, errors='coerce')

# Drop rows with missing values
df.dropna(inplace=True)

# === Model Training ===
X = df[features]
y = df[target]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train XGBoost Model
model = XGBRegressor(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42)
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, "power_prediction_xgboost_model.pkl")
print("✅ Model saved as 'power_prediction_xgboost_model.pkl'")

# === Evaluation ===
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

print(f"\n📈 R² Score: {r2:.4f}")
print(f"📉 MSE: {mse:.2f}")
print(f"📉 RMSE: {rmse:.2f}\n")

# === Plotting Actual vs Predicted ===
plt.figure(figsize=(10, 6))
plt.plot(y_test.values[:50], label="Actual", marker='o')
plt.plot(y_pred[:50], label="Predicted", marker='x')
plt.title("Power Prediction: Actual vs Predicted (XGBoost)")
plt.xlabel("Sample Index")
plt.ylabel("Power")
plt.legend()
plt.grid(True)

# Save plot
plt.savefig("power_prediction_xgboost_plot.png")
print("📊 Plot saved as 'power_prediction_xgboost_plot.png'")