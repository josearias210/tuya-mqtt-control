import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import unittest
from unittest.mock import patch, MagicMock

# Patch environment variable before importing tuya_control
DUMMY_DEVICES = '[{"id": "dev1", "ip": "192.168.1.10", "key": "abc123"}]'
os.environ["TUYA_DEVICES"] = DUMMY_DEVICES

# Remove tuya_control from sys.modules if already imported (for test reruns)
sys.modules.pop("tuya_control", None)
from src import tuya_control

class TestTuyaBulbControlActions(unittest.TestCase):
    def setUp(self):
        self.device_id = 'dev1'
        self.device_info = {'id': 'dev1', 'ip': '192.168.1.10', 'key': 'abc123'}
        tuya_control.DEVICES = {self.device_id: self.device_info}

    @patch('tinytuya.BulbDevice')
    def test_control_bulb_on(self, MockBulbDevice):
        mock_device = MagicMock()
        MockBulbDevice.return_value = mock_device
        tuya_control.TuyaBulbController(tuya_control.DEVICES).control_bulb(self.device_id, True)
        mock_device.set_status.assert_any_call('white', 21)
        mock_device.set_status.assert_any_call(True, 20)

    @patch('tinytuya.BulbDevice')
    def test_control_bulb_off(self, MockBulbDevice):
        mock_device = MagicMock()
        MockBulbDevice.return_value = mock_device
        tuya_control.TuyaBulbController(tuya_control.DEVICES).control_bulb(self.device_id, False)
        mock_device.set_status.assert_called_with(False, 20)
        # No debe llamar a set_status('white', 21) al apagar
        calls = [call[0][0] for call in mock_device.set_status.call_args_list]
        self.assertNotIn('white', calls)

    @patch('tinytuya.BulbDevice')
    def test_set_brightness(self, MockBulbDevice):
        mock_device = MagicMock()
        MockBulbDevice.return_value = mock_device
        tuya_control.TuyaBulbController(tuya_control.DEVICES).set_brightness(self.device_id, 128)
        mock_device.set_brightness.assert_called_with(128)

    @patch('tinytuya.BulbDevice')
    def test_set_color_name(self, MockBulbDevice):
        mock_device = MagicMock()
        MockBulbDevice.return_value = mock_device
        tuya_control.TuyaBulbController(tuya_control.DEVICES).set_color(self.device_id, 'red')
        mock_device.set_colour.assert_called_with(255, 0, 0)

    @patch('tinytuya.BulbDevice')
    def test_set_color_json_rgb(self, MockBulbDevice):
        mock_device = MagicMock()
        MockBulbDevice.return_value = mock_device
        color_json = '{"r":10,"g":20,"b":30}'
        tuya_control.TuyaBulbController(tuya_control.DEVICES).set_color(self.device_id, color_json)
        mock_device.set_colour.assert_called_with(10, 20, 30)

    @patch('tinytuya.BulbDevice')
    def test_set_color_json_hsv(self, MockBulbDevice):
        mock_device = MagicMock()
        MockBulbDevice.return_value = mock_device
        color_json = '{"h":0,"s":1000,"v":1000}'
        tuya_control.TuyaBulbController(tuya_control.DEVICES).set_color(self.device_id, color_json)
        mock_device.set_colour.assert_called_with(255, 0, 0)

if __name__ == '__main__':
    unittest.main()
