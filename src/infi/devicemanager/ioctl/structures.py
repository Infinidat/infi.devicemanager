from infi.instruct import ULInt64, ULInt32, ULInt16, ULInt8
from infi.instruct import Struct

def is_64bit():
    import sys
    return sys.maxsize > 2 ** 32

POINTER = ULInt64 if is_64bit() else ULInt32
WORD = ULInt16
DWORD = ULInt32
BYTE = ULInt8

class SCSI_ADDRESS(Struct):
    _fields_ = [DWORD("Length"), BYTE("PortNumber"), BYTE("PathId"), BYTE("TargetId"), BYTE("Lun")]

DEVICE_TYPE = DWORD

class STORAGE_DEVICE_NUMBER(Struct):
    _fields_ = [DEVICE_TYPE("DeviceType"), DWORD("DeviceNumber"), DWORD("PartitionNumber")]

