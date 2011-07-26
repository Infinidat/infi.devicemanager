
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
    size = SCSI_ADDRESS.sizeof()
    instance = SCSI_ADDRESS.create_instance_from_string('\x00' * size)
    instance.Length = SCSI_ADDRESS.sizeof()
    string = c_buffer(SCSI_ADDRESS.instance_to_string(instance), size)
    _ = ioctl(handle, IOCTL_SCSI_GET_ADDRESS, 0, 0, string, size)
    return SCSI_ADDRESS.create_instance_from_string(string)

def ioctl_storage_get_device_number(handle):
    from .structures import STORAGE_DEVICE_NUMBER
    from .constants import IOCTL_STORAGE_GET_DEVICE_NUMBER
    from ctypes import c_buffer
    size = STORAGE_DEVICE_NUMBER.sizeof()
    string = c_buffer('\x00' * size, size)
    _ = ioctl(handle, IOCTL_STORAGE_GET_DEVICE_NUMBER, 0, 0, string, size)
    return STORAGE_DEVICE_NUMBER.create_instance_from_string(string)

class DeviceIoControl(object):
    def __init__(self, device_path):
        super(DeviceIoControl, self).__init__()
        self.device_path = device_path

    def scsi_get_address(self):
        with open_handle(self.device_path) as handle:
            return ioctl_scsi_get_address(handle)

    def storage_get_device_number(self):
        with open_handle(self.device_path) as handle:
            return ioctl_storage_get_device_number(handle)
