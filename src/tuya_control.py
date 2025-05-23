"""
app.py

Tuya Smart Bulb device controller via MQTT.

- Allows turning on/off, adjusting brightness and color of Tuya bulbs.
- Exposes control and state via MQTT.
- Device configuration via TUYA_DEVICES environment variable (JSON).

Author: Antonio
License: MIT
"""

import os
import json
import logging
from tuya_bulb_controller import TuyaBulbController
from mqtt_manager import MqttManager
from dotenv import load_dotenv

# --- Device and MQTT Configuration ---
# New: Read devices from environment variables like TUYA_DEVICES_1_id, TUYA_DEVICES_1_ip, etc.
def load_devices_from_env():
    load_dotenv()
    devices = []
    i = 0
    while True:
        id_ = os.getenv(f'TUYA_DEVICES_{i}_ID')
        ip = os.getenv(f'TUYA_DEVICES_{i}_IP')
        key = os.getenv(f'TUYA_DEVICES_{i}_KEY')
        if not id_ or not ip or not key:
            break
        devices.append({'id': id_, 'ip': ip, 'key': key})
        i += 1
    return devices

devices_list = load_devices_from_env()
if not devices_list:
    # Fallback to TUYA_DEVICES (JSON array) only if there are no individual variables
    DEVICES_JSON = os.getenv("TUYA_DEVICES")
    if not DEVICES_JSON:
        raise RuntimeError("Environment variable TUYA_DEVICES or TUYA_DEVICES_1_id/_ip/_key is required.")
    try:
        devices_list = json.loads(DEVICES_JSON)
        if not isinstance(devices_list, list):
            raise ValueError("TUYA_DEVICES must be a JSON array of device objects.")
    except Exception as e:
        raise RuntimeError(f"Invalid TUYA_DEVICES JSON: {e}")

DEVICES = {d["id"]: d for d in devices_list if "id" in d and "ip" in d and "key" in d}
if not DEVICES:
    raise ValueError("No valid devices found. Each device must have 'id', 'ip', and 'key'.")

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

# --- Main Function ---
def main():
    logging.basicConfig(level=logging.INFO)
    bulb_controller = TuyaBulbController(DEVICES)
    mqtt_manager = MqttManager(MQTT_BROKER, MQTT_PORT, DEVICES, bulb_controller)
    mqtt_manager.start()

if __name__ == "__main__":
    main()