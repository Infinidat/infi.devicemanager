from infi.cwrap import WrappedFunction, IN, OUT, IN_OUT
from ctypes import c_void_p, c_ulong, c_long
from infi.exceptools import InfiException

HANDLE = c_void_p
HWND = HANDLE
DWORD = c_ulong
BOOL = c_long

class WindowsException(InfiException):
    def __init__(self, errno):
        from ctypes import FormatError
        self.winerror = errno
        self.strerror = FormatError(errno)

    def __repr__(self):
        return "%s, %s" % (self.winerror, self.strerror)

    def __str__(self):
        return self.__repr__()

def errcheck_invalid_handle():
    from .constants import INVALID_HANDLE_VALUE
    from ctypes import GetLastError
    def errcheck(result, func, args):
        if result == INVALID_HANDLE_VALUE:
            raise WindowsException(GetLastError())
        return result
    return errcheck

def errcheck_bool():
    from ctypes import GetLastError
    def errcheck(result, func, args):
        if result == 0:
            raise WindowsException(GetLastError())
        return result
    return errcheck

class Function(WrappedFunction):
    return_value = BOOL

    @classmethod
    def get_errcheck(cls):
        return errcheck_bool()

    @classmethod
    def get_library_name(cls):
        return 'setupapi'

    @classmethod
    def get_parameters(cls):
        pass

class SetupDiGetClassDevsW(Function):
    return_value = HANDLE

    @classmethod
    def get_errcheck(cls):
        return errcheck_invalid_handle()

    @classmethod
    def get_parameters(cls):
        return ((c_void_p, IN, "ClassGuid"), (c_void_p, IN, "Enumerator"),
                (HWND, IN, "hwndParent"), (DWORD, IN, "Flags"))

class SetupDiEnumDeviceInfo(Function):
    return_value = BOOL

    @classmethod
    def get_errcheck(cls):
        return errcheck_bool()

    @classmethod
    def get_parameters(cls):
        return ((HANDLE, IN, "DeviceInfoSet"), (DWORD, IN, "MemberIndex"),
                (c_void_p, IN_OUT, "DeviceInfoData"))

class SetupDiGetDevicePropertyKeys(Function):
    @classmethod
    def get_parameters(cls):
        return ((HANDLE, IN, "DeviceInfoSet"),
                (c_void_p, IN, "DeviceInfoData"),
                (c_void_p, IN_OUT, "PropertyKeyArray"),
                (DWORD, IN, "PropertyKeyCount"),
                (c_void_p, IN_OUT, "RequeiredPropertyKeyCount"),
                (DWORD, IN, "Flags"))

class SetupDiGetDevicePropertyW(Function):
    @classmethod
    def get_parameters(cls):
        return ((HANDLE, IN, "DeviceInfoSet"),
                (c_void_p, IN, "DeviceInfoData"),
                (c_void_p, IN, "PropertyKey"),
                (c_void_p, IN_OUT, "PropertyType"),
                (c_void_p, IN_OUT, "PropertyBuffer"),
                (DWORD, IN, "PropertyBufferSize"),
                (c_void_p, IN_OUT, "RequiredSize"),
                (DWORD, IN, "Flags"))

class SetupDiDestroyDeviceInfoList(Function):
    @classmethod
    def get_parameters(cls):
        return ((HANDLE, IN, "DeviceInfoSet"),)

class SetupDiOpenDeviceInfoW(Function):
    @classmethod
    def get_parameters(cls):
        return ((HANDLE, IN, "DeviceInfoSet"),
                (c_void_p, IN, "DeviceInstanceId"),
                (HWND, IN, "parent"),
                (DWORD, IN, "OpenFlags"),
                (c_void_p, IN_OUT, "DeviceInfoData"))

class SetupDiCreateDeviceInfoList(Function):
    return_value = HANDLE

    @classmethod
    def get_errcheck(cls):
        return errcheck_invalid_handle()

    @classmethod
    def get_parameters(cls):
        return ((c_void_p, IN, "ClassGuid"),
                (HWND, IN, "parent",))

class ConvertStringSecurityDescriptorToSecurityDescriptorW(WrappedFunction):
    return_value = BOOL

    @classmethod
    def get_errcheck(cls):
        return errcheck_bool()

    @classmethod
    def get_library_name(cls):
        return 'advapi32'

    @classmethod
    def get_parameters(cls):
        return ((c_void_p, IN, "StringSecurityDescriptor"),
                (DWORD, IN, "StringSDRevision"),
                (c_void_p, IN_OUT, "SecurityDescriptor"),
                (c_void_p, IN_OUT, "SecurityDescriptorSize"))
