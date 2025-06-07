import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import joblib
import matplotlib
import numpy as np

# Use non-GUI backend for plotting
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# === Load and Clean the Data ===
df = pd.read_csv("merged_telemetry_data.csv")

# Define features and target
features = ['battery', 'current', 'irradiance', 'panel_tilt', 'temperature', 'voltage']
target = 'power'

# Keep only relevant columns
df = df[['timestamp'] + features + [target]]

# Convert to numeric
df[features + [target]] = df[features + [target]].apply(pd.to_numeric, errors='coerce')

# Drop missing values
df.dropna(inplace=True)

# === Train-Test Split ===
X = df[features]
y = df[target]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === Train Linear Regression Model ===
model = LinearRegression()
model.fit(X_train, y_train)

# Save the model
joblib.dump(model, "power_prediction_lr_model.pkl")
print("✅ Model saved as 'power_prediction_lr_model.pkl'")

# === Evaluation ===
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)       
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)

print(f"\n📈 R² Score: {r2:.4f}")
print(f"📉 MSE: {mse:.2f}")
print(f"📉 RMSE: {rmse:.2f}\n")

# === Visualization ===
plt.figure(figsize=(10, 6))
plt.plot(y_test.values[:50], label="Actual", marker='o')
plt.plot(y_pred[:50], label="Predicted", marker='x')
plt.title("Linear Regression: Power Prediction (Actual vs Predicted)")
plt.xlabel("Sample Index")
plt.ylabel("Power")
plt.legend()
plt.grid(True)
plt.savefig("lr_power_prediction_plot.png")
print("📊 Plot saved as 'lr_power_prediction_plot.png'")