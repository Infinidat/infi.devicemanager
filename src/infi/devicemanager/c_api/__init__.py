from infi.crap import WrappedFunction, IN, OUT, IN_OUT
from ctypes import c_void_p, c_ulong

HANDLE = c_void_p
HWND = HANDLE
DWORD = c_ulong

class Function(WrappedFunction):
    retun_value = None

    @classmethod
    def get_library_name(cls):
        return 'setupapi'

    @classmethod
    def get_parameters(cls):
        pass

def errcheck_invalid_handle():
    from .constants import INVALID_HANDLE_VALUE

    def errcheck(result, func, args):
        from ctypes import GetLastError, WinError
        if result == INVALID_HANDLE_VALUE:
            raise WinError(GetLastError)
        return args

    return errcheck

class SetupDiGetClassDevsA(Function):
    return_value = HANDLE

    @classmethod
    def get_errcheck(cls):
        return errcheck_invalid_handle()

    @classmethod
    def get_parameters(cls):
        return ((c_void_p, IN, "ClassGuid"), (c_void_p, IN, "Enumerator"),
                (HWND, IN, "hwndParent"), (DWORD, IN, "Flags"))

