from infi.wioctl.structures import *
from infi.instruct import VarSizeArray, ReadPointer

class SCSI_ADDRESS(Struct):
    _fields_ = [DWORD("Length"), BYTE("PortNumber"), BYTE("PathId"), BYTE("TargetId"), BYTE("Lun")]

DEVICE_TYPE = DWORD

class STORAGE_DEVICE_NUMBER(Struct):
    _fields_ = [DEVICE_TYPE("DeviceType"), DWORD("DeviceNumber"), DWORD("PartitionNumber")]

class DISK_GEOMETRY(Struct):
    _fields_ = [Field("Cylinders", LARGE_INTEGER), DWORD("MediaType"),
                DWORD("TracksPerCylinder"), DWORD("SectorsPerTrack"), DWORD("BytesPerSector")]

class DISK_GEOMETRY_EX(Struct):
    _fields_ = [Field("Geometry", DISK_GEOMETRY), Field("DiskSize", LARGE_INTEGER),
               ]# it is actually a variable-length structure, but we don't care about the rest

class DISK_EXTENT(Struct):
    _fields_ = [DWORD("DiskNumber"), DWORD("Padding"), Field("StartingOffset", LARGE_INTEGER),
                Field("ExtentLength", LARGE_INTEGER)]

class VOLUME_DISK_EXTENTS(Struct):
    _fields_ = [DWORD("NumberOfDiskExtents"), DWORD("Padding"),
                VarSizeArray("Extents", ReadPointer("NumberOfDiskExtents"), DISK_EXTENT)]
