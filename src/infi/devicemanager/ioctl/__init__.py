
import infi.wioctl
from . import structures, constants
from infi.exceptools import chain
import ctypes

def ioctl_scsi_get_address(handle):
    size = _sizeof(structures.SCSI_ADDRESS)
    instance = structures.SCSI_ADDRESS.create_from_string(b'\x00' * size)
    instance.Length = size
    string = ctypes.c_buffer(structures.SCSI_ADDRESS.write_to_string(instance), size).raw
    try:
        _ = infi.wioctl.ioctl(handle, infi.wioctl.constants.IOCTL_SCSI_GET_ADDRESS, 0, 0, string, size)
    except infi.wioctl.errors.WindowsException as exception:
        if exception.winerror == infi.wioctl.constants.ERROR_ACCESS_DENIED:
            raise chain(infi.wioctl.errors.InvalidHandle(exception.winerror))
    instance = structures.SCSI_ADDRESS.create_from_string(string)
    return (instance.PortNumber, instance.PathId, instance.TargetId, instance.Lun)

def ioctl_storage_get_device_number(handle):
    size = _sizeof(structures.STORAGE_DEVICE_NUMBER)
    string = ctypes.c_buffer(b'\x00' * size, size).raw
    _ = infi.wioctl.ioctl(handle, infi.wioctl.constants.IOCTL_STORAGE_GET_DEVICE_NUMBER, 0, 0, string, size)
    instance = structures.STORAGE_DEVICE_NUMBER.create_from_string(string)
    return (instance.DeviceNumber, instance.PartitionNumber,)

def ioctl_disk_get_drive_geometry_ex(handle):
    size = _sizeof(structures.DISK_GEOMETRY_EX)
    string = ctypes.c_buffer(b'\x00' * size, size).raw
    try:
        # this IOCTL expects a variable-length buffer for storing infomation about partitions
        # we don't care about that, so we send a short buffer on purpose. this raises an exception
        _ = infi.wioctl.ioctl(handle, infi.wioctl.constants.IOCTL_DISK_GET_DRIVE_GEOMETRY_EX, 0, 0, string, size)
    except infi.wioctl.api.WindowsException as e:
        if e.winerror != infi.wioctl.constants.ERROR_INSUFFICIENT_BUFFER:
            raise
    instance = structures.DISK_GEOMETRY_EX.create_from_string(string).DiskSize
    return instance.QuadPart if structures.is_64bit() else (instance.HighPart << 32) + instance.LowPart

def ioctl_volume_get_volume_disk_extents(handle):
    size = structures.VOLUME_DISK_EXTENTS.min_max_sizeof().min + _sizeof(structures.DISK_EXTENT)
    string = ctypes.c_buffer('\x00' * size, size)
    try:
        infi.wioctl.ioctl(handle, infi.wioctl.constants.IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS, 0, 0, string, size)
    except infi.wioctl.api.WindowsException as e:
        if e.winerror != infi.wioctl.constants.ERROR_MORE_DATA:
            raise
    count = structures.DWORD.create_from_string(string)
    size = size + ((count - 1) * _sizeof(structures.DISK_EXTENT))
    string = ctypes.c_buffer('\x00' * size, size)
    infi.wioctl.ioctl(handle, infi.wioctl.constants.IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS, 0, 0, string, size)
    instance = structures.VOLUME_DISK_EXTENTS.create_from_string(string)
    return instance.Extents

def _sizeof(struct):
    return struct.min_max_sizeof().max

class DeviceIoControl(infi.wioctl.DeviceIoControl):
    def scsi_get_address(self):
        """:returns: a tuple (host, channel, target, lun)"""
        with infi.wioctl.open_handle(self.device_path) as handle:
            return ioctl_scsi_get_address(handle)

    def storage_get_device_number(self):
        """:returns: the %d from PhysicalDriveX"""
        with infi.wioctl.open_handle(self.device_path) as handle:
            return ioctl_storage_get_device_number(handle)[0]

    def storage_get_device_and_partition_number(self):
        with infi.wioctl.open_handle(self.device_path) as handle:
            return ioctl_storage_get_device_number(handle)

    def disk_get_drive_geometry_ex(self):
        """:returns: size in bytes of device"""
        with infi.wioctl.open_handle(self.device_path) as handle:
            return ioctl_disk_get_drive_geometry_ex(handle)

    def get_volume_disk_extents(self):
        with infi.wioctl.open_handle(self.device_path) as handle:
            return ioctl_volume_get_volume_disk_extents(handle)
