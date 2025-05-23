import tinytuya
import colorsys
import json
import logging
from typing import Dict, Any

class TuyaBulbController:
    """
    Encapsulates the logic for controlling Tuya bulbs.
    """
    def __init__(self, devices: Dict[str, dict]):
        self.devices = devices

    def get_device(self, device_id: str) -> tinytuya.BulbDevice:
        d = self.devices.get(device_id)
        if not d:
            raise RuntimeError(f"Device {device_id} not found in configuration.")
        dev = tinytuya.BulbDevice(d["id"], d["ip"], d["key"])
        dev.set_version(3.4)
        return dev

    def control_bulb(self, device_id: str, turn_on: bool) -> None:
        dev = self.get_device(device_id)
        # Only set white when turning on, not when turning off
        if turn_on:
            dev.set_status('white', 21)
        dev.set_status(turn_on, 20)
        logging.info(f"Bulb {device_id} {'turned on' if turn_on else 'turned off'} successfully.")

    def set_brightness(self, device_id: str, brightness: int) -> None:
        dev = self.get_device(device_id)
        dev.set_brightness(brightness)
        logging.info(f"Bulb {device_id} brightness set to {brightness}.")

    def set_color(self, device_id: str, color: str) -> None:
        dev = self.get_device(device_id)
        try:
            if color.strip().startswith('{'):
                color_value = json.loads(color)
                if all(k in color_value for k in ('r', 'g', 'b')):
                    dev.set_colour(color_value['r'], color_value['g'], color_value['b'])
                elif all(k in color_value for k in ('h', 's', 'v')):
                    h = color_value['h'] / 360.0
                    s = color_value['s'] / 1000.0
                    v = color_value['v'] / 1000.0
                    r, g, b = [int(x * 255) for x in colorsys.hsv_to_rgb(h, s, v)]
                    dev.set_colour(r, g, b)
                else:
                    logging.error("JSON color must have 'r','g','b' or 'h','s','v'")
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
                        dev.set_white(255, 1000)
                    else:
                        dev.set_colour(*rgb)
                else:
                    logging.error(f"Unknown color name: {color}")
                    return
        except Exception as e:
            logging.error(f"set_color failed: {e}")
            return
        logging.info(f"Bulb {device_id} color set to {color}.")

    def get_device_status(self, device_id: str) -> Dict[str, Any]:
        dev = self.get_device(device_id)
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
            logging.error(f"Getting status for {device_id}: {e}")
            return {'error': str(e)}
