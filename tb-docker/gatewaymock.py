import paho.mqtt.client as mqtt
import json
import random
import time

# ThingsBoard Gateway MQTT Broker
THINGSBOARD_HOST = "localhost"
GATEWAY_TOKEN = "uHsHxNLeoLqHHD73qDd6"

# List of virtual device names
DEVICE_NAMES = [
    "Voltage",
    "Current",
    "Power",
    "Irradiance",
    "Temperature",
    "Battery",
    "Panel_tilt"
]

# Setup MQTT client
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.username_pw_set(GATEWAY_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)

# Function to generate mock telemetry
def generate_realistic_data():
    Voltage = round(random.uniform(10.5, 14.5), 2)
    Current = round(random.uniform(2.0, 5.0), 2)
    power_noise = random.uniform(-5.0, 5.0)
    Power = round((Voltage * Current) + power_noise, 2)
    Irradiance = round(random.uniform(200.0, 1000.0), 2)
    Temperature = round(random.uniform(20.0, 40.0), 2)
    Battery = round(random.uniform(20.0, 100.0), 2)
    Panel_tilt = round(random.uniform(0.0, 90.0), 2)

    return {
        "Voltage": Voltage,
        "Current": Current,
        "Power": Power,
        "Irradiance": Irradiance,
        "Temperature": Temperature,
        "Battery": Battery,
        "Panel_tilt": Panel_tilt
    }

# Connect each virtual device
for device_name in DEVICE_NAMES:
    connect_payload = json.dumps({ "device": device_name })
    client.publish("v1/gateway/connect", connect_payload)
    print(f"Connected virtual device: {device_name}")
    time.sleep(0.5)

# Send telemetry loop
try:
    while True:
        sensor_data = generate_realistic_data()

        for device_name in DEVICE_NAMES:
            value = sensor_data[device_name]
            telemetry_payload = {
                device_name: [ { device_name: value } ]
            }
            client.publish("v1/gateway/telemetry", json.dumps(telemetry_payload))
            print(f"Sent telemetry for {device_name}: {value}")
            time.sleep(0.2)

        time.sleep(2)

except KeyboardInterrupt:
    print("\nStopping gateway client...")
    client.disconnect()
