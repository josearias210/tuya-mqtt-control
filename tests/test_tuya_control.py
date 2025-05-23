import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Patch environment variable before importing tuya_control
DUMMY_DEVICES = '[{"id": "dev1", "ip": "192.168.1.10", "key": "abc123"}]'
os.environ["TUYA_DEVICES"] = DUMMY_DEVICES

# Remove tuya_control from sys.modules if already imported (for test reruns)
sys.modules.pop("tuya_control", None)
from src import tuya_control

class TestTuyaControl(unittest.TestCase):
    def setUp(self):
        self.device_id = 'dev1'
        self.device_info = {'id': 'dev1', 'ip': '192.168.1.10', 'key': 'abc123'}
        tuya_control.DEVICES = {self.device_id: self.device_info}

    @patch('tinytuya.BulbDevice')
    def test_get_device_success(self, MockBulbDevice):
        mock_device = MagicMock()
        MockBulbDevice.return_value = mock_device
        device = tuya_control.get_device(self.device_id)
        self.assertEqual(device, mock_device)
        MockBulbDevice.assert_called_with('dev1', '192.168.1.10', 'abc123')
        mock_device.set_version.assert_called_with(3.4)

    def test_get_device_not_found(self):
        with self.assertRaises(RuntimeError):
            tuya_control.get_device('unknown')

if __name__ == '__main__':
    unittest.main()
