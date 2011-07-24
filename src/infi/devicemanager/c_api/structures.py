from infi.instruct import ULInt32, ULInt16, ULInt8
from infi.instruct import Struct, FixedSizeArray
from ctypes import c_void_p

WORD = ULInt16
DWORD = ULInt32
BYTE = ULInt8

class GUID(Struct):
    _fields_ = [DWORD("Data1"), WORD("Data2"), WORD("Data3"), FixedSizeArray("Data4", 8, BYTE)]
