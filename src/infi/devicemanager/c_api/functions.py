
from ctypes import c_buffer
from .constants import DIGCF_PRESENT
from .structures import GUID

def pretty_string_to_guid(pretty_string):
    from binascii import unhexlify
    guid = GUID.create_instance_from_string(unhexlify(''.join(pretty_string.strip("{}").split('-'))))
    return guid

def SetupDiGetClassDevs(guid_string, enumerator_string='', parent_handle=0, flags=DIGCF_PRESENT):
    pass
