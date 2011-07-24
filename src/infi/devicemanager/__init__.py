__import__("pkg_resources").declare_namespace(__name__)


"""
SetupDiGetClassDevs
SetupDiEnumDeviceInfo
SetupDiGetDeviceRegistryProperty
"""

class Device(object):
    pass

class DeviceManager(object):
    def __init__(self):
        super(DeviceManager, self).__init__()

    @property
    def disk_drives(self):
        yield

    @property
    def storage_controller(self):
        yield
