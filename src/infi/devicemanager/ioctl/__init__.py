
from contextlib import contextmanager

@contextmanager
def open_handle(device_path):
    from .api import CreateFileW, CloseHandle
    from ctypes import create_unicode_buffer
    from constants import FILE_SHARE_READ, FILE_SHARE_WRITE, OPEN_EXISTING
    handle = None
    try:
        handle = CreateFileW(create_unicode_buffer(device_path),
                             0, FILE_SHARE_READ | FILE_SHARE_WRITE,
                             0, OPEN_EXISTING, 0, 0)
        yield handle
    finally:
        if handle is not None:
            CloseHandle(handle)

def ioctl(handle, control_code, in_buffer, in_buffer_size, out_buffer, out_buffer_size):
    from ctypes import byref, c_ulong
    from .api import DeviceIoControl as interface
    bytes_returned = c_ulong()
    interface(handle, control_code, in_buffer, in_buffer_size, out_buffer, out_buffer_size,
                    byref(bytes_returned), 0)
    return bytes_returned.value

def ioctl_scsi_get_address(handle):
    from .structures import SCSI_ADDRESS
    from .constants import IOCTL_SCSI_GET_ADDRESS
    from ctypes import c_buffer
    size = SCSI_ADDRESS.min_max_sizeof().max
    instance = SCSI_ADDRESS.create_from_string('\x00' * size)
    instance.Length = SCSI_ADDRESS.min_max_sizeof().max
    string = c_buffer(SCSI_ADDRESS.write_to_string(instance), size)
    _ = ioctl(handle, IOCTL_SCSI_GET_ADDRESS, 0, 0, string, size)
    instance = SCSI_ADDRESS.create_from_string(string)
    return (instance.PortNumber, instance.PathId, instance.TargetId, instance.Lun)

def ioctl_storage_get_device_number(handle):
    from .structures import STORAGE_DEVICE_NUMBER
    from .constants import IOCTL_STORAGE_GET_DEVICE_NUMBER
    from ctypes import c_buffer
    size = STORAGE_DEVICE_NUMBER.min_max_sizeof().max
    string = c_buffer('\x00' * size, size)
    _ = ioctl(handle, IOCTL_STORAGE_GET_DEVICE_NUMBER, 0, 0, string, size)
    instance = STORAGE_DEVICE_NUMBER.create_from_string(string)
    return instance.DeviceNumber

def ioctl_disk_get_drive_geometry_ex(handle):
    from .structures import DISK_GEOMETRY_EX, is_64bit
    from .constants import IOCTL_DISK_GET_DRIVE_GEOMETRY_EX
    from .api import WindowsException
    from ctypes import c_buffer
    size = DISK_GEOMETRY_EX.min_max_sizeof().max
    string = c_buffer('\x00' * size, size)
    try:
        # this IOCTL expects a variable-length buffer for storing infomation about partitions
        # we don't care about that, so we send a short buffer on purpose. this raises an exception
        _ = ioctl(handle, IOCTL_DISK_GET_DRIVE_GEOMETRY_EX, 0, 0, string, size)
    except WindowsException, e:
        # TODO finer grained exception handling
        pass
    instance = DISK_GEOMETRY_EX.create_from_string(string).DiskSize
    return instance.QuadPart if is_64bit() else instance.HighPart << 32 + instance.LowPart

class DeviceIoControl(object):
    def __init__(self, device_path):
        super(DeviceIoControl, self).__init__()
        self.device_path = device_path

    def scsi_get_address(self):
        """returns a tuple (host, channel, target, lun)"""
        with open_handle(self.device_path) as handle:
            return ioctl_scsi_get_address(handle)

    def storage_get_device_number(self):
        """returns the %d from PhysicalDriveX"""
        with open_handle(self.device_path) as handle:
            return ioctl_storage_get_device_number(handle)

    def disk_get_drive_geometry_ex(self):
        """returns size in bytes of device"""
        with open_handle(self.device_path) as handle:
            return ioctl_disk_get_drive_geometry_ex(handle)

