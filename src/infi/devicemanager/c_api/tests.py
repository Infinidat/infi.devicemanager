
import unittest
import mock

class GuidTestCase(unittest.TestCase):
    def test_create_from_string(self):
        from .functions import pretty_string_to_guid
        from .constants import SCSIADAPTER_GUID_STRING
        guid = pretty_string_to_guid(SCSIADAPTER_GUID_STRING)
        self.assertEqual(guid.Data1, 0x7BE9364D)
        self.assertEqual(guid.Data2, 0x25E3)
        self.assertEqual(guid.Data3, 0xCE11)
        self.assertEqual(guid.Data4, [0xBF, 0xC1, 0x08, 0x00, 0x2B, 0xE1, 0x03, 0x18])
