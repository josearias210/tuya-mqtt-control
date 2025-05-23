"""
tuya_control.py

Tuya Smart Bulb device controller via MQTT.

- Allows turning on/off, adjusting brightness and color of Tuya bulbs.
- Exposes control and state via MQTT.
- Device configuration via TUYA_DEVICES environment variable (JSON).

Author: Antonio
License: MIT
"""

import os
import json
import colorsys
import tinytuya
import paho.mqtt.client as mqtt
from typing import Optional, Dict, Any

# --- Device and MQTT Configuration ---

DEVICES_JSON = os.getenv("TUYA_DEVICES")
if not DEVICES_JSON:
    raise RuntimeError("Environment variable TUYA_DEVICES is required and must be a valid JSON list of devices.")

try:
    devices_list = json.loads(DEVICES_JSON)
    if not isinstance(devices_list, list):
        raise ValueError("TUYA_DEVICES must be a JSON array of device objects.")
    DEVICES = {d["id"]: d for d in devices_list if "id" in d and "ip" in d and "key" in d}
    if not DEVICES:
        raise ValueError("No valid devices found in TUYA_DEVICES. Each device must have 'id', 'ip', and 'key'.")
except Exception as e:
    raise RuntimeError(f"Invalid TUYA_DEVICES JSON: {e}")

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

mqtt_client: Optional[mqtt.Client] = None

# --- Main Device Control Functions ---

def get_device(device_id: str) -> tinytuya.BulbDevice:
    """
    Returns a BulbDevice instance for the specified device.
    """
    d = DEVICES.get(device_id)
    if not d:
        raise RuntimeError(f"Device {device_id} not found in configuration.")
    dev = tinytuya.BulbDevice(d["id"], d["ip"], d["key"])
    dev.set_version(3.4)
    return dev

def control_bulb(device_id: str, turn_on: bool) -> None:
    """
    Turns the specified bulb on or off.
    """
    print(f"[ACTION] {'ON' if turn_on else 'OFF'} command sent to device {device_id}")
    dev = get_device(device_id)
    dev.set_status('white', 21)  # Set to white mode
    dev.set_status(turn_on, 20)  # Power on/off
    print(f"Bulb {device_id} {'turned on' if turn_on else 'turned off'} successfully.")
    publish_real_status(device_id)

def set_brightness(device_id: str, brightness: int) -> None:
    """
    Sets the brightness of the bulb.
    """
    print(f"[ACTION] Set BRIGHTNESS {brightness} for device {device_id}")
    dev = get_device(device_id)
    dev.set_brightness(brightness)
    print(f"Bulb {device_id} brightness set to {brightness}.")
    publish_real_status(device_id)

def set_color(device_id: str, color: str) -> None:
    """
    Sets the color of the bulb. Accepts color name or JSON with RGB/HSV.
    """
    print(f"[ACTION] Set COLOR {color} for device {device_id}")
    dev = get_device(device_id)
    try:
        if color.strip().startswith('{'):
            color_value = json.loads(color)
            # RGB
            if all(k in color_value for k in ('r', 'g', 'b')):
                dev.set_colour(color_value['r'], color_value['g'], color_value['b'])
            # HSV
            elif all(k in color_value for k in ('h', 's', 'v')):
                h = color_value['h'] / 360.0
                s = color_value['s'] / 1000.0
                v = color_value['v'] / 1000.0
                r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(h, s, v)]
                dev.set_colour(r, g, b)
            else:
                print("[ERROR] JSON color must have 'r','g','b' or 'h','s','v'")
                return
        else:
            color_map = {
                'red': (255, 0, 0),
                'green': (0, 255, 0),
                'blue': (0, 0, 255),
                'yellow': (255, 255, 0),
                'cyan': (0, 255, 255),
                'magenta': (255, 0, 255),
                'white': (255, 255, 255),
                'orange': (255, 165, 0),
                'purple': (128, 0, 128),
            }
            rgb = color_map.get(color.lower())
            if rgb:
                if color.lower() == 'white' and hasattr(dev, 'set_white'):
                    dev.set_white(255, 1000)  # Max brightness, neutral temperature
                else:
                    dev.set_colour(*rgb)
            else:
                print(f"[ERROR] Unknown color name: {color}")
                return
    except Exception as e:
        print(f"[ERROR] set_color failed: {e}")
        return
    print(f"Bulb {device_id} color set to {color}.")
    publish_real_status(device_id)

def get_device_status(device_id: str) -> Dict[str, Any]:
    """
    Gets the current status of the device.
    """
    dev = get_device(device_id)
    try:
        status = dev.status()
        is_on = status.get('dps', {}).get('20')
        brightness = status.get('dps', {}).get('22')
        color = status.get('dps', {}).get('24')
        return {
            'on': is_on,
            'brightness': brightness,
            'color': color,
            'raw': status
        }
    except Exception as e:
        print(f"[ERROR] Getting status for {device_id}: {e}")
        return {'error': str(e)}

def publish_real_status(device_id: str) -> None:
    """
    Publishes the real status of the device to MQTT.
    """
    status = get_device_status(device_id)
    if mqtt_client:
        topic = f"/device/{device_id}/light/status"
        mqtt_client.publish(topic, json.dumps(status), retain=True)

# --- MQTT Callbacks ---

def on_connect(client, userdata, flags, rc):
    """
    MQTT connection callback.
    """
    print("Connected to MQTT with result code " + str(rc))
    for device_id in DEVICES:
        client.subscribe(f"/device/{device_id}/light/on")
        client.subscribe(f"/device/{device_id}/light/off")
        client.subscribe(f"/device/{device_id}/light/brightness")
        client.subscribe(f"/device/{device_id}/light/color")
        client.subscribe(f"/device/{device_id}/light/status/request")

def on_message(client, userdata, msg):
    """
    MQTT message received callback.
    """
    topic = msg.topic
    payload = msg.payload.decode()
    print(f"[MESSAGE] Received '{payload}' on topic '{topic}'")
    parts = topic.split('/')
    if len(parts) < 5:
        print("[ERROR] Topic format invalid.")
        return
    device_id = parts[2]
    action = parts[4]
    try:
        if action == "on":
            control_bulb(device_id, True)
        elif action == "off":
            control_bulb(device_id, False)
        elif action == "brightness":
            value = int(payload)
            set_brightness(device_id, value)
        elif action == "color":
            set_color(device_id, payload)
        elif action == "request":
            publish_real_status(device_id)
    except Exception as e:
        print(f"[ERROR] Handling message: {e}")

# --- Main Function ---

def main():
    """
    Initializes the MQTT client and enters the main loop.
    """
    global mqtt_client
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    print(f"Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...")
    mqtt_client.loop_forever()

if __name__ == "__main__":
    main()