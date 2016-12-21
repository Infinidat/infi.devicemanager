__import__("pkg_resources").declare_namespace(__name__)

from contextlib import contextmanager
from infi.exceptools import chain
from .setupapi import functions, properties, constants
from .ioctl import DeviceIoControl
from infi.pyutils.lazy import cached_method
from logging import getLogger

ROOT_INSTANCE_ID = u"HTREE\\ROOT\\0"
GLOBALROOT = u"\\\\?\\GLOBALROOT"
logger = getLogger(__name__)


class Device(object):
    def __init__(self, instance_id):
        super(Device, self).__init__()
        self._instance_id = instance_id

    def __repr__(self):
        # we cant use hasattr and getattr here, because friendly_name is a property method that may raise exception
        return u"<{}>".format(self.friendly_name if self.has_property("friendly_name") else self.description)

    @contextmanager
    def _open_handle(self):
        dis, devinfo = None, None
        try:
            dis = functions.SetupDiCreateDeviceInfoList()
            devinfo = functions.SetupDiOpenDeviceInfo(dis, self._instance_id)
            yield (dis, devinfo)
        finally:
            if dis is not None:
                functions.SetupDiDestroyDeviceInfoList(dis)

    def _get_setupapi_property(self, key):
        from .setupapi import WindowsException
        with self._open_handle() as handle:
            dis, devinfo = handle
            try:
                return functions.SetupDiGetDeviceProperty(dis, devinfo, key).python_object
            except WindowsException as exception:
                if exception.winerror == constants.ERROR_NOT_FOUND:
                    raise KeyError(key)
                chain(exception)

    @property
    @cached_method
    def class_guid(self):
        guid = self._get_setupapi_property(properties.DEVPKEY_Device_ClassGuid)
        return functions.guid_to_pretty_string(guid)

    @property
    @cached_method
    def description(self):
        try:
            return self._get_setupapi_property(properties.DEVPKEY_Device_DeviceDesc)
        except KeyError:
            return 'description unavailable'

    @property
    @cached_method
    def hardware_ids(self):
        return self._get_setupapi_property(properties.DEVPKEY_Device_HardwareIds)

    @property
    @cached_method
    def instance_id(self):
        return self._get_setupapi_property(properties.DEVPKEY_Device_InstanceId)

    @property
    @cached_method
    def psuedo_device_object(self):
        value = self._get_setupapi_property(properties.DEVPKEY_Device_PDOName)
        if value is None:
            raise KeyError(properties.DEVPKEY_Device_PDOName)
        return GLOBALROOT + value

    @property
    @cached_method
    def friendly_name(self):
        return self._get_setupapi_property(properties.DEVPKEY_Device_FriendlyName)

    @property
    @cached_method
    def location_paths(self):
        return self._get_setupapi_property(properties.DEVPKEY_Device_LocationPaths)

    @property
    @cached_method
    def location(self):
        return self._get_setupapi_property(properties.DEVPKEY_Device_LocationInfo)

    @property
    @cached_method
    def bus_number(self):
        return self._get_setupapi_property(properties.DEVPKEY_Device_BusNumber)

    @property
    @cached_method
    def ui_number(self):
        return self._get_setupapi_property(properties.DEVPKEY_Device_UINumber)

    @property
    @cached_method
    def address(self):
        return self._get_setupapi_property(properties.DEVPKEY_Device_Address)

    @property
    def children(self):
        children = []
        items = []
        try:
            items = self._get_setupapi_property(properties.DEVPKEY_Device_Children)
        except KeyError:
            pass
        for instance_id in items:
            children.append(Device(instance_id))
        return children

    @property
    def parent(self):
        instance_id = self._get_setupapi_property(properties.DEVPKEY_Device_Parent)
        return Device(instance_id)

    @property
    @cached_method
    def instance_id(self):
        return self._instance_id

    @property
    @cached_method
    def devnode_status(self):
        return self._get_setupapi_property(properties.DEVPKEY_Device_DevNodeStatus)

    def is_root(self):
        return self._instance_id == ROOT_INSTANCE_ID

    def is_real_device(self):
        return self.has_property("location")

    def is_iscsi_device(self):
        return any("iscsi" in hardware_id.lower() for hardware_id in self.hardware_ids)

    def is_hidden(self):
        return bool(self.devnode_status & constants.DN_NO_SHOW_IN_DM)

    def has_property(self, name):
        try:
            _ = getattr(self, name)
            return True
        except KeyError:
            pass
        return False

    @cached_method
    def get_available_property_ids(self):
        result = []
        with self._open_handle() as handle:
            dis, devinfo = handle
            guid_list = functions.SetupDiGetDevicePropertyKeys(dis, devinfo)
            for guid in guid_list:
                result.append(functions.guid_to_pretty_string(guid))
        return result

    def rescan(self):
        from .cfgmgr32 import open_handle, CM_Reenumerate_DevNode_Ex
        if not self.is_real_device() and not self.is_iscsi_device():
            return
        with open_handle(self._instance_id) as handle:
            machine_handle, device_handle = handle
            _ = CM_Reenumerate_DevNode_Ex(device_handle, 0, machine_handle)


class DeviceManager(object):
    def __init__(self):
        super(DeviceManager, self).__init__()
        self._dis_list = []

    def __repr__(self):
        return "<DeviceManager>"

    @contextmanager
    def _open_handle(self, guid_string):
        dis = None
        try:
            dis = functions.SetupDiGetClassDevs(guid_string)
            yield dis
        finally:
            if dis is not None:
                functions.SetupDiDestroyDeviceInfoList(dis)

    def get_devices_from_handle(self, handle):
        devices = []
        for devinfo in functions.SetupDiEnumDeviceInfo(handle):
            try:
                instance_id = functions.SetupDiGetDeviceProperty(handle, devinfo, properties.DEVPKEY_Device_InstanceId)
            except:
                logger.exception("failed to get DEVPKEY_Device_InstanceId from device {!r} by handle {!r}".format(handle, devinfo))
                continue
            devices.append(Device(instance_id.python_object))
        return devices

    @property
    def all_devices(self):
        with self._open_handle(None) as handle:
            return self.get_devices_from_handle(handle)

    @property
    def disk_drives(self):
        disk_drives = []
        for controller in self.storage_controllers:
            def match_class_guid(device):
                try:
                    return device.class_guid == constants.GENDISK_GUID_STRING
                except:
                    return False
            disk_drives.extend(filter(match_class_guid, controller.children))
        return disk_drives

    @property
    def storage_controllers(self):
        with self._open_handle(constants.SCSIADAPTER_GUID_STRING) as handle:
            return self.get_devices_from_handle(handle)

    @property
    def scsi_devices(self):
        devices = []
        with self._open_handle(constants.SCSIADAPTER_GUID_STRING) as handle:
            storage_controllers = self.get_devices_from_handle(handle)
            for controller in storage_controllers:
                if not controller.has_property("children"):
                    continue
                devices.extend(controller.children)
        return devices

    @property
    def volumes(self):
        with self._open_handle(constants.GENVOLUME_GUID_STRING) as handle:
            return self.get_devices_from_handle(handle)

    @property
    def root(self):
        return Device(ROOT_INSTANCE_ID)
