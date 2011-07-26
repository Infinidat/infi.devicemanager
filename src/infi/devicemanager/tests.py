
import unittest
import mock

from . import DeviceManager
from .ioctl import DeviceIoControl

class TestCase(unittest.TestCase):
    def setUp(self):
        from os import name
        if name != "nt":
            raise unittest.SkipTest

    def test_all_devices(self):
        dm = DeviceManager()
        devices = dm.all_devices
        self.assertGreater(len(devices), 0)

    def test_storage_controllers(self):
        dm = DeviceManager()
        devices = dm.storage_controllers
        self.assertLess(len(devices), 10)
        self.assertGreater(len(devices), 0)
        scsi_devices = []
        for controller in devices:
            scsi_devices.extend(controller.description)

    def test_disks(self):
        dm = DeviceManager()
        devices = dm.disk_drives
        self.assertGreater(len(devices), 0)
        for disk in devices:
            scsi_address = DeviceIoControl(disk.psuedo_device_object).scsi_get_address()
            device_number = DeviceIoControl(disk.psuedo_device_object).storage_get_device_number()

    def test_list_properties(self):
        dm = DeviceManager()
        devices = dm.all_devices
        for device in devices:
            prop_list = device.get_available_property_ids()
            self.assertGreater(len(prop_list), 0)
            self.assertIsInstance(prop_list[0], str)

    def test_rescan__storage(self):
        dm = DeviceManager()
        for device in dm.storage_controllers:
            device.rescan()

    def test_scsi_devices(self):
        dm = DeviceManager()
        devices = dm.scsi_devices
        self.assertGreater(len(devices), 0)
