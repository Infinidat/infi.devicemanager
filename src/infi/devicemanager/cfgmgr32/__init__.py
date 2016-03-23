
from infi.cwrap import WrappedFunction, IN, IN_OUT
from ctypes import c_buffer, create_unicode_buffer, byref, c_ulong, c_void_p

DWORD = c_ulong
CONFIGRET = DWORD
PDEVINST = c_void_p
ULONG = c_ulong
HANDLE = c_void_p
HMACHINE = HANDLE

CR_SUCCESS = 0
CM_LOCATE_DEVNODE_NORMAL = 0X00000000
CM_LOCATE_DEVNODE_PHANTOM = 0X00000001
CM_LOCATE_DEVNODE_CANCELREMOVE = 0X00000002
CM_LOCATE_DEVNODE_NOVALIDATION = 0X00000004
CM_LOCATE_DEVNODE_BITS = 0X00000007

CM_REENUMERATE_NORMAL = 0x00000000
CM_REENUMERATE_SYNCHRONOUS = 0x00000001
CM_REENUMERATE_RETRY_INSTALLATION = 0x00000002
CM_REENUMERATE_ASYNCHRONOUS = 0x00000004
CM_REENUMERATE_BITS = 0x00000007

def errcheck():
    def errcheck(result, func, args):
        if result != CR_SUCCESS:
            raise RuntimeError(result)
        return result
    return errcheck

class Function(WrappedFunction):
    return_value = CONFIGRET

    @classmethod
    def get_errcheck(cls):
        return errcheck()

    @classmethod
    def get_library_name(cls):
        return 'cfgmgr32'

    @classmethod
    def get_parameters(cls):
        pass

class CM_Connect_MachineW(Function):
    @classmethod
    def get_parameters(cls):
        return ((c_void_p, IN, "UNCServerName"),
                (c_void_p, IN_OUT, "hMachine"))

class CM_Disconnect_Machine(Function):
    @classmethod
    def get_parameters(cls):
        return ((c_void_p, IN, "hMachine"),)

class CM_Locate_DevNode_ExW(Function):
    @classmethod
    def get_parameters(cls):
        return ((c_void_p, IN_OUT, "dnDevInst"),
                (c_void_p, IN, "DeviceID"),
                (c_ulong, IN, "ulFlags"),
                (HMACHINE, IN, "hMachine"))

class CM_Reenumerate_DevNode_Ex(Function):
    @classmethod
    def get_parameters(cls):
        return ((c_void_p, IN_OUT, "dnDevInst"),
                (c_ulong, IN, "ulFlags"),
                (HMACHINE, IN, "hMachine"))

def CM_Connect_Machine():
    handle = c_void_p()
    _ = CM_Connect_MachineW(0, byref(handle))
    return handle

def CM_Locate_DevNode(machine_handle, instance_id):
    device_handle = c_void_p()
    _ = CM_Locate_DevNode_ExW(byref(device_handle), create_unicode_buffer(instance_id),
                             0, machine_handle)
    return device_handle

from contextlib import contextmanager

@contextmanager
def open_handle(instance_id):
    machine_handle, device_handle = None, None
    try:
        machine_handle = CM_Connect_Machine()
        device_handle = CM_Locate_DevNode(machine_handle, instance_id)
        yield (machine_handle, device_handle)
    finally:
        if machine_handle is not None:
            _ = CM_Disconnect_Machine(machine_handle)
