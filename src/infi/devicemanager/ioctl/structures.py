from infi.instruct import ULInt64, ULInt32, ULInt16, ULInt8, Field, FixedSizeArray
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

class LARGE_INTEGER(Struct):
    _fields_ = [ULInt64("QuadPart"), ] if is_64bit() else [DWORD("LowPart"), DWORD("HighPart")]

class DISK_GEOMETRY(Struct):
    _fields_ = [Field("Cylinders", LARGE_INTEGER), DWORD("MediaType"),
                DWORD("TracksPerCylinder"), DWORD("SectorsPerTrack"), DWORD("BytesPerSector")]

class DISK_GEOMETRY_EX(Struct):
    _fields_ = [Field("Geometry", DISK_GEOMETRY), Field("DiskSize", LARGE_INTEGER),
               ]# it is actually a variable-length structure, but we don't care about the rest
