import json
import logging
import paho.mqtt.client as mqtt
from typing import Dict
from tuya_bulb_controller import TuyaBulbController

class MqttManager:
    """
    Encapsulates the logic for MQTT connection and callbacks.
    """
    def __init__(self, broker: str, port: int, devices: Dict[str, dict], bulb_controller: TuyaBulbController):
        self.broker = broker
        self.port = port
        self.devices = devices
        self.bulb_controller = bulb_controller
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def start(self):
        logging.info(f"Connecting to MQTT broker {self.broker}:{self.port} ...")
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()

    def publish_real_status(self, device_id: str) -> None:
        status = self.bulb_controller.get_device_status(device_id)
        topic = f"/device/{device_id}/light/status"
        self.client.publish(topic, json.dumps(status), retain=True)

    def on_connect(self, client, userdata, flags, rc):
        logging.info(f"Connected to MQTT with result code {rc}")
        for device_id in self.devices:
            client.subscribe(f"/device/{device_id}/light/on")
            client.subscribe(f"/device/{device_id}/light/off")
            client.subscribe(f"/device/{device_id}/light/brightness")
            client.subscribe(f"/device/{device_id}/light/color")
            client.subscribe(f"/device/{device_id}/light/status/request")

    def on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()
        logging.info(f"[MESSAGE] Received '{payload}' on topic '{topic}'")
        parts = topic.split('/')
        if len(parts) < 5:
            logging.error("Topic format invalid.")
            return
        device_id = parts[2]
        action = parts[4]
        try:
            if action == "on":
                self.bulb_controller.control_bulb(device_id, True)
            elif action == "off":
                self.bulb_controller.control_bulb(device_id, False)
            elif action == "brightness":
                value = int(payload)
                self.bulb_controller.set_brightness(device_id, value)
            elif action == "color":
                self.bulb_controller.set_color(device_id, payload)
            elif action == "request":
                self.publish_real_status(device_id)
        except Exception as e:
            logging.error(f"Handling message: {e}")
