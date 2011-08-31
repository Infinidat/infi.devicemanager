from infi.instruct import ULInt64, ULInt32, ULInt16, ULInt8
from infi.instruct import Struct, FixedSizeArray, Padding, Field
from ctypes import c_void_p

def is_64bit():
    import sys
    return sys.maxsize > 2 ** 32

POINTER = ULInt64 if is_64bit() else ULInt32
WORD = ULInt16
DWORD = ULInt32
BYTE = ULInt8

class GUID(Struct):
    _fields_ = [DWORD("Data1"), WORD("Data2"), WORD("Data3"), FixedSizeArray("Data4", 8, BYTE)]

class SP_DEVINFO_DATA(Struct):
    _fields_ = [DWORD("cbSize"), # 4
                Field("ClassGuid", GUID),
                DWORD("DevInst"), # 24
                POINTER("Reserved") # 28 or 32
                ]

DEVPROPGUID = GUID
DEVPROPID = DWORD
DEVPROPTYPE = DWORD

class DEVPROPKEY(GUID):
    _fields_ = GUID._fields_ + [DEVPROPID("pid")]

    def __eq__(self, other):
        if not isinstance(other, DEVPROPKEY):
            return False
        for attr in ["pid", "Data1", "Data2", "Data3", "Data4"]:
            if getattr(self, attr) != getattr(other, attr):
                return False
        return True

class FILETIME(Struct):
    _fields_ = [DWORD("dwLowDateTime"), DWORD("dwHighDateTime")]

SECURITY_DESCRIPTOR_CONTROL = WORD

class SECURITY_DESCRIPTOR(Struct):
    _fields_ = [BYTE("Revision"), BYTE("Sbz1"), SECURITY_DESCRIPTOR_CONTROL("Control"),
                DWORD("Owner"), DWORD("Group"), DWORD("Sacl"), DWORD("Dacl")]

class SCSI_ADDRESS(Struct):
    _fields_ = [DWORD("Length"), BYTE("PortNumber"), BYTE("PathId"), BYTE("TargetId"), BYTE("Lun")]

DEVICE_TYPE = DWORD

class STORAGE_DEVICE_NUMBER(Struct):
    _fields_ = [DEVICE_TYPE("DeviceType"), DWORD("DeviceNumber"), DWORD("PartitionNumber")]

