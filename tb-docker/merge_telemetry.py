import pandas as pd
import glob
import os

folder_path = "exported_telemetry_data"
dataframes = []

csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

if not csv_files:
    print("❌ No CSV files found in 'exported_telemetry' folder.")
else:
    print(f"🔍 Found {len(csv_files)} CSV file(s):")
    for filepath in csv_files:
        print(" -", filepath)

# 📥 Load each CSV and add device name
for filepath in csv_files:
    try:
        df = pd.read_csv(filepath)
        df.columns = [col.strip().lower().replace(" ", "").replace("_", "") for col in df.columns]

        # Standardize timestamp
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", errors="coerce")
            df = df.dropna(subset=["timestamp"])
            df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%dT%H:%M:%S.%f")
        else:
            print(f"⛔ No timestamp column in {filepath}")
            continue

        # Add column for device name
        device_name = os.path.basename(filepath).split(".")[0].lower()
        df["device"] = device_name

        # Assign measurement to its own column
        value_col = [col for col in df.columns if col not in ["timestamp", "device"]]
        if len(value_col) != 1:
            print(f"⚠ Expected 1 measurement column in {filepath}, found: {value_col}")
            continue
        df = df[["timestamp", "device", value_col[0]]]
        df.columns = ["timestamp", "device", "value"]

        dataframes.append(df)

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")

# 🔄 Merge and Pivot
if dataframes:
    long_df = pd.concat(dataframes, ignore_index=True)

    # Pivot to wide format
    pivot_df = long_df.pivot_table(index="timestamp", columns="device", values="value", aggfunc="first").reset_index()

    # ✅ Clean column names
    pivot_df.columns.name = None
    pivot_df.sort_values("timestamp", inplace=True)

    pivot_df.to_csv("merged_telemetry_data.csv", index=False)
    print("\n✅ Merged and pivoted CSV saved as 'merged_telemetry_data.csv'")
else:
    print("❌ No valid data found.")