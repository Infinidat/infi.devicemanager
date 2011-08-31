
from infi.crap import WrappedFunction, IN, IN_OUT
from ctypes import c_void_p, c_ulong

HANDLE = c_void_p
DWORD = c_ulong
BOOL = c_ulong

class WindowsException(Exception):
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

class CreateFileW(WrappedFunction):
    return_value = HANDLE

    @classmethod
    def get_errcheck(cls):
        return errcheck_invalid_handle()

    @classmethod
    def get_library_name(cls):
        return 'kernel32'

    @classmethod
    def get_parameters(cls):
        return ((c_void_p, IN, "FileName"),
                (DWORD, IN, "DesiredAccess"),
                (DWORD, IN, "SharedMode"),
                (c_void_p, IN, "SecurityAttributes"),
                (DWORD, IN, "CreationDisposition"),
                (DWORD, IN, "FlagsAndAttributes"),
                (HANDLE, IN_OUT, "TemplateFile"))

class DeviceIoControl(WrappedFunction):
    return_value = BOOL

    @classmethod
    def get_errcheck(cls):
        return errcheck_bool()

    @classmethod
    def get_library_name(cls):
        return 'kernel32'

    @classmethod
    def get_parameters(cls):
        return ((HANDLE, IN, "Device"),
                (DWORD, IN, "ControlCode"),
                (c_void_p, IN, "InputBuffer"),
                (DWORD, IN, "InputBufferSize"),
                (c_void_p, IN_OUT, "OutBuffer"),
                (DWORD, IN, "OutBufferSize"),
                (c_void_p, IN_OUT, "BytesReturned"),
                (c_void_p, IN_OUT, "Overldappped"))

class CloseHandle(WrappedFunction):
    return_value = BOOL

    @classmethod
    def get_errcheck(cls):
        return errcheck_bool()

    @classmethod
    def get_library_name(cls):
        return 'kernel32'

    @classmethod
    def get_parameters(cls):
        return ((HANDLE, IN, "Device"),)
