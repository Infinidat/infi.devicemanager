
from infi import unittest
from logging import getLogger

log = getLogger()

class StructuresTestCase(unittest.TestCase):
    def test_guid_converison(self):
        from .functions import pretty_string_to_guid, guid_to_pretty_string
        from .constants import SCSIADAPTER_GUID_STRING as pretty_string
        self.assertEqual(pretty_string,
                         guid_to_pretty_string(pretty_string_to_guid(pretty_string)))

    def test_sizes(self):
        from .structures import GUID, SP_DEVINFO_DATA, is_64bit
        self.assertEqual(GUID.min_max_sizeof().max, 16)
        self.assertEqual(SP_DEVINFO_DATA.min_max_sizeof().max, 32 if is_64bit() else 28)

class FunctionTestCase(unittest.TestCase):
    def setUp(self):
        from os import name
        if name != 'nt':
            raise unittest.SkipTest

    def test_SetupDiGetClassDevs(self):
        from .functions import SetupDiGetClassDevs
        from .constants import SCSIADAPTER_GUID_STRING
        result = SetupDiGetClassDevs(SCSIADAPTER_GUID_STRING)

    def test_SetupDiEnumDeviceInfo(self):
        from .functions import SetupDiGetClassDevs, SetupDiEnumDeviceInfo
        devinfo_list = [info for info in SetupDiEnumDeviceInfo(SetupDiGetClassDevs())]
        self.assertGreater(len(devinfo_list), 0)

    def test_SetupDiGetDevicePropertyKeys(self):
        from .functions import SetupDiGetClassDevs, SetupDiEnumDeviceInfo, SetupDiGetDevicePropertyKeys
        device_info_set = SetupDiGetClassDevs()
        dev_info_data_list = [info for info in SetupDiEnumDeviceInfo(device_info_set)]
        property_keys = SetupDiGetDevicePropertyKeys(device_info_set, dev_info_data_list[10])
        self.assertGreater(len(property_keys), 0)

    def test_SetupdiGetDeviceProperty__string(self):
        from .functions import SetupDiGetClassDevs, SetupDiEnumDeviceInfo
        from .functions import SetupDiGetDevicePropertyKeys, SetupDiGetDeviceProperty
        device_info_set = SetupDiGetClassDevs()
        dev_info_data_list = [info for info in SetupDiEnumDeviceInfo(device_info_set)]
        property_keys = SetupDiGetDevicePropertyKeys(device_info_set, dev_info_data_list[10])
        property = SetupDiGetDeviceProperty(device_info_set, dev_info_data_list[10], property_keys[0])
        value = property.python_object

    def test_SetupdiGetDeviceProperty__all_found(self):
        from .functions import SetupDiGetClassDevs, SetupDiEnumDeviceInfo
        from .functions import SetupDiGetDevicePropertyKeys, SetupDiGetDeviceProperty
        device_info_set = SetupDiGetClassDevs()
        for devinfo in SetupDiEnumDeviceInfo(device_info_set):
            for key in SetupDiGetDevicePropertyKeys(device_info_set, devinfo):
                log.debug(key)
                property = SetupDiGetDeviceProperty(device_info_set, devinfo, key)
                value = property.python_object
