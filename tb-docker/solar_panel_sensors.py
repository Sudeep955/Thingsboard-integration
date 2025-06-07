import paho.mqtt.client as mqtt
import json
import random
import time

# ThingsBoard MQTT Broker
THINGSBOARD_HOST = "localhost"  # Update if using an external ThingsBoard host

# Device tokens (replace with actual tokens)
DEVICE_TOKENS = {
    "Voltage": "7xylAeDDoZkzNNIayuIr",
    "Current": "O7urOrQCMCAi5Y9Uk5Hf",
    "Power": "Op6E5bclBbY4LKH8L2Ym",
    "Irradiance": "Dcg2IwZZ8Uos2NGrvQVI",
    "Temperature": "xTYlwMU6gXDbSCZJ9WD4",
    "Battery": "c0ZtxaCoWZn0bGvhgB4M",
    "Panel_tilt": "gyDIhLu51KbDIFn2SGYn"
}

# Create MQTT clients for each device
clients = {}
for device, token in DEVICE_TOKENS.items():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)  # MQTT v2 API
    client.username_pw_set(token)
    client.connect(THINGSBOARD_HOST, 1883, 60)
    clients[device] = client

# Generate realistic sensor data
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

# Send data every 5 seconds
try:
    while True:
        sensor_data = generate_realistic_data()

        for sensor, value in sensor_data.items():
            if sensor in clients:
                payload = json.dumps({sensor: value})
                clients[sensor].publish("v1/devices/me/telemetry", payload)
                print(f"Sent to {sensor}: {payload}")
        
        time.sleep(5)

except KeyboardInterrupt:
    print("\nStopping script... Disconnecting clients.")
    for client in clients.values():
        client.disconnect()
        