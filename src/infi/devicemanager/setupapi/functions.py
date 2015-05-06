
from infi.exceptools import chain
from infi.pyutils.decorators import wraps
from ctypes import c_buffer, byref
from .constants import DIGCF_PRESENT, DIGCF_ALLCLASSES, DIOD_INHERIT_CLASSDRVS
from .constants import ERROR_NO_MORE_ITEMS, ERROR_BAD_COMMAND, ERROR_INSUFFICIENT_BUFFER
from .structures import GUID
from .structures import DEVPROPKEY, SP_DEVINFO_DATA
from . import DWORD, WindowsException

from logging import getLogger
log = getLogger()

def pretty_string_to_guid(pretty_string):
    from binascii import unhexlify
    pretty_string = ''.join(pretty_string.strip("{}").split('-'))
    pretty_string = pretty_string[0:8][::-1] + pretty_string[8:12][::-1] + \
                    pretty_string[12:16][::-1] + pretty_string[16:]
    pretty_string = pretty_string[0:2][::-1] + pretty_string[2:4][::-1] + pretty_string[4:6][::-1] + \
                    pretty_string[6:8][::-1] + pretty_string[8:10][::-1] + pretty_string[10:12][::-1] + \
                    pretty_string[12:14][::-1] + pretty_string[14:16][::-1] + pretty_string[16:]
    guid = GUID.create_from_string(unhexlify(pretty_string))
    return guid

def guid_to_pretty_string(guid):
    from binascii import hexlify
    pretty_string = hexlify(GUID.write_to_string(guid)).upper().decode('ASCII')
    pretty_string = pretty_string[0:2][::-1] + pretty_string[2:4][::-1] + pretty_string[4:6][::-1] + \
                    pretty_string[6:8][::-1] + pretty_string[8:10][::-1] + pretty_string[10:12][::-1] + \
                    pretty_string[12:14][::-1] + pretty_string[14:16][::-1] + pretty_string[16:]
    pretty_string = pretty_string[0:8][::-1] + pretty_string[8:12][::-1] + \
                    pretty_string[12:16][::-1] + pretty_string[16:]
    return '-'.join([pretty_string[:8], pretty_string[8:12], pretty_string[12:16],
                     pretty_string[16:20], pretty_string[20:]])

def SetupDiGetClassDevs(guid_string=None, enumerator_string=None, parent_handle=0, flags=DIGCF_PRESENT):
    from . import SetupDiGetClassDevsW as interface
    from ctypes import create_unicode_buffer
    if guid_string is not None:
        guid = pretty_string_to_guid(guid_string)
        guid_buffer = c_buffer(GUID.write_to_string(guid), GUID.min_max_sizeof().max)
    else:
        flags = flags | DIGCF_ALLCLASSES
        guid_buffer = 0
    enumerator_buffer = 0 if enumerator_string is None else create_unicode_buffer(enumerator_string)
    return interface(guid_buffer, enumerator_buffer, parent_handle, flags)

def generator(decorated_func):
    @wraps(decorated_func)
    def callee(*args, **kwargs):
        from . import WindowsException
        index = 0
        while True:
            try:
                kwargs["index"] = index
                yield decorated_func(*args, **kwargs)
                index += 1
            except WindowsException as exception:
                if exception.winerror in [ERROR_NO_MORE_ITEMS, ERROR_BAD_COMMAND]: # TODO why ERROR_BAD_COMMAND?
                    raise StopIteration
                chain(exception)
    return callee

@generator
def SetupDiEnumDeviceInfo(device_info_set, index=0):
    from . import SetupDiEnumDeviceInfo as interface
    device_info_data = SP_DEVINFO_DATA.create_from_string(b'\x00' * SP_DEVINFO_DATA.min_max_sizeof().max)
    device_info_data.cbSize = SP_DEVINFO_DATA.min_max_sizeof().max
    device_info_buffer = c_buffer(SP_DEVINFO_DATA.write_to_string(device_info_data), SP_DEVINFO_DATA.min_max_sizeof().max).raw
    interface(device_info_set, index, device_info_buffer)
    return SP_DEVINFO_DATA.create_from_string(device_info_buffer)

def SetupDiGetDevicePropertyKeys(device_info_set, devinfo_data):
    from .structures import FixedSizeArray, Struct
    from . import SetupDiGetDevicePropertyKeys as interface

    required_key_count = DWORD()
    device_info_buffer = c_buffer(SP_DEVINFO_DATA.write_to_string(devinfo_data), SP_DEVINFO_DATA.min_max_sizeof().max)
    try:
        interface(device_info_set, device_info_buffer, 0, 0, byref(required_key_count), 0)
    except WindowsException as exception:
        if exception.winerror != ERROR_INSUFFICIENT_BUFFER:
            raise

    class PropertyKeyArray(Struct):
        _fields_ = [FixedSizeArray("keys", required_key_count.value, DEVPROPKEY)]

    keys_buffer = c_buffer(b'\x00' * PropertyKeyArray.min_max_sizeof().max, PropertyKeyArray.min_max_sizeof().max).raw
    interface(device_info_set, device_info_buffer, keys_buffer, required_key_count,
              byref(required_key_count), 0)
    return PropertyKeyArray.create_from_string(keys_buffer).keys

def SetupDiGetDeviceProperty(device_info_set, devinfo_data, property_key):
    from . import SetupDiGetDevicePropertyW as interface

    value_type = DWORD()
    required_size = DWORD()
    device_info_buffer = c_buffer(SP_DEVINFO_DATA.write_to_string(devinfo_data), SP_DEVINFO_DATA.min_max_sizeof().max)
    property_key_buffer = c_buffer(DEVPROPKEY.write_to_string(property_key), DEVPROPKEY.min_max_sizeof().max)
    try:
        interface(device_info_set, device_info_buffer, property_key_buffer, byref(value_type),
                  0, 0, byref(required_size), 0)
    except WindowsException as exception:
        if exception.winerror != ERROR_INSUFFICIENT_BUFFER:
            raise

    value_buffer = c_buffer(required_size.value)
    interface(device_info_set, device_info_buffer, property_key_buffer, byref(value_type),
              value_buffer, required_size, byref(required_size), 0)
    return Property(value_buffer.raw, value_type.value, property_key)

def SetupDiOpenDeviceInfo(device_info_set, instance_id, flags=DIOD_INHERIT_CLASSDRVS):
    from . import SetupDiOpenDeviceInfoW as interface
    from ctypes import create_unicode_buffer

    instance_id_buffer = create_unicode_buffer(instance_id)
    device_info_data = SP_DEVINFO_DATA.create_from_string(b'\x00' * SP_DEVINFO_DATA.min_max_sizeof().max)
    device_info_data.cbSize = SP_DEVINFO_DATA.min_max_sizeof().max
    device_info_buffer = c_buffer(SP_DEVINFO_DATA.write_to_string(device_info_data), SP_DEVINFO_DATA.min_max_sizeof().max).raw
    interface(device_info_set, instance_id_buffer, 0, flags, device_info_buffer)
    return SP_DEVINFO_DATA.create_from_string(device_info_buffer)

def SetupDiCreateDeviceInfoList(guid_string=None):
    from . import SetupDiCreateDeviceInfoList as interface
    if guid_string is not None:
        guid = pretty_string_to_guid(guid_string)
        guid_buffer = c_buffer(GUID.write_to_string(guid), GUID.min_max_sizeof().max)
    else:
        guid_buffer = 0
    return interface(guid_buffer, 0)

from . import SetupDiDestroyDeviceInfoList

class Property(object):
    def __init__(self, value_buffer, value_type, key):
        self._buffer = value_buffer
        self._type = value_type
        self._object = None
        self._key = key

    @property
    def python_object(self):
        if self._object is None:
            self._object = self._get_python_object()
        return self._object

    def _get_python_object(self):
        from . import properties
        from .structures import Struct, FixedSizeArray, ULInt32, ULInt8
        from .structures import FILETIME, SECURITY_DESCRIPTOR
        from . import ConvertStringSecurityDescriptorToSecurityDescriptorW as ConvertSDDL
        from .constants import SDDL_REVISION_1
        if self._type in [properties.DEVPROP_TYPE_STRING]:
            return self._buffer.decode("utf-16")[:-1]
        if self._type in [properties.DEVPROP_TYPE_STRING_LIST]:
            return self._buffer.decode("utf-16")[:-1].split(chr(0))[:-1]
        if self._type in [properties.DEVPROP_TYPE_GUID]:
            return GUID.create_from_string(self._buffer)
        if self._type in [properties.DEVPROP_TYPE_UINT32,
                          properties.DEVPROP_TYPE_ERROR,
                          properties.DEVPROP_TYPE_NTSTATUS]:
            class Value(Struct):
                _fields_ = [ULInt32("value")]
            return Value.create_from_string(self._buffer).value
        if self._type in [properties.DEVPROP_TYPE_BINARY]:
            class Value(Struct):
                _fields_ = [FixedSizeArray("value", len(self._buffer), ULInt8)]
            return Value.create_from_string(self._buffer).value
        if self._type in [properties.DEVPROP_TYPE_BOOLEAN]:
            class Value(Struct):
                _fields_ = [ULInt8("value")]
            return Value.create_from_string(self._buffer).value != 0
        if self._type in [properties.DEVPROP_TYPE_FILETIME]:
            return FILETIME.create_from_string(self._buffer)
        if self._type in [properties.DEVPROP_TYPE_SECURITY_DESCRIPTOR]:
            return SECURITY_DESCRIPTOR.create_from_string(self._buffer)
        if self._type in [properties.DEVPROP_TYPE_SECURITY_DESCRIPTOR_STRING]:
            sd_buffer = c_buffer('\x00' * SECURITY_DESCRIPTOR.min_max_sizeof().max)
            ConvertSDDL(c_buffer(self._buffer), SDDL_REVISION_1, sd_buffer, 0)
            # TODO requires to call LocalFree
            return SECURITY_DESCRIPTOR.create_from_string(sd_buffer)
        log = debug("{!r}. {!r}, {!r}".format(self._buffer, self._type, self._key))
        raise ValueError(self._buffer, self._type)
