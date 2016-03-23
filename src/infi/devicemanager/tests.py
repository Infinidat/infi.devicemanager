
import unittest
import sys

from . import DeviceManager
from .ioctl import DeviceIoControl

if sys.version_info[0] == 2:
    _STRING_INSTANCE = basestring
else:
    _STRING_INSTANCE = str


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
        from infi.wioctl.errors import WindowsException
        dm = DeviceManager()
        devices = dm.disk_drives
        self.assertGreater(len(devices), 0)
        for disk in devices:
            scsi_address = DeviceIoControl(disk.psuedo_device_object).scsi_get_address()
            device_number = DeviceIoControl(disk.psuedo_device_object).storage_get_device_number()
            self.assertTrue(isinstance(device_number, int) or isinstance(device_number, long))
            try:
                size = DeviceIoControl(disk.psuedo_device_object).disk_get_drive_geometry_ex()
                self.assertTrue(isinstance(size, int) or isinstance(size, long))
            except WindowsException as error:
                if error.winerror == 1:
                    # If there is MPIO disk, we cannot do IOCTLs on underlying SCSI disks
                    continue
                else:
                    raise

    def test_list_properties(self):
        dm = DeviceManager()
        devices = dm.all_devices
        for device in devices:
            prop_list = device.get_available_property_ids()
            self.assertGreater(len(prop_list), 0)
            self.assertIsInstance(prop_list[0], _STRING_INSTANCE)

    def test_rescan__storage(self):
        dm = DeviceManager()
        for device in dm.storage_controllers:
            device.rescan()

    def test_scsi_devices(self):
        dm = DeviceManager()
        devices = dm.scsi_devices
        self.assertGreater(len(devices), 0)

    def test_children_on_device_with_no_children(self):
        dm = DeviceManager()
        for device in dm.disk_drives:
            self.assertEqual(len(device.children), 0)

    def test_disk_drives_instance_ids(self):
        dm = DeviceManager()
        for device in dm.disk_drives:
            instance_id = device._instance_id
            self.assertFalse(instance_id.isupper())
