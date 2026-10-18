"""Entry stand-in: create a named Job Object with KILL_ON_JOB_CLOSE, assign ITSELF to it, then launch a cell with shell=True whose command
starts a grandchild loop writing a counter to MARKER. Print JOB <name> and READY, then sleep."""
import ctypes
import ctypes.wintypes as wt
import subprocess
import sys
import time

name, marker = sys.argv[1], sys.argv[2]
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.CreateJobObjectW.restype = wt.HANDLE
k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wt.LPCWSTR]
k32.SetInformationJobObject.argtypes = [wt.HANDLE, ctypes.c_int, ctypes.c_void_p, wt.DWORD]
k32.AssignProcessToJobObject.argtypes = [wt.HANDLE, wt.HANDLE]
k32.GetCurrentProcess.restype = wt.HANDLE


class BASIC(ctypes.Structure):
    _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64), ("LimitFlags", wt.DWORD),
                ("MinimumWorkingSetSize", ctypes.c_size_t), ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wt.DWORD),
                ("Affinity", ctypes.c_size_t), ("PriorityClass", wt.DWORD), ("SchedulingClass", wt.DWORD)]


class IOC(ctypes.Structure):
    _fields_ = [(n, ctypes.c_uint64) for n in ("a", "b", "c", "d", "e", "f")]


class EXT(ctypes.Structure):
    _fields_ = [("Basic", BASIC), ("Io", IOC), ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]


h = k32.CreateJobObjectW(None, name)
if not h:
    print("CREATE_FAIL", ctypes.get_last_error(), flush=True)
    sys.exit(3)
ext = EXT()
ext.Basic.LimitFlags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
if not k32.SetInformationJobObject(h, 9, ctypes.byref(ext), ctypes.sizeof(ext)):  # JobObjectExtendedLimitInformation
    print("SETINFO_FAIL", ctypes.get_last_error(), flush=True)
    sys.exit(3)
if not k32.AssignProcessToJobObject(h, k32.GetCurrentProcess()):
    print("ASSIGN_FAIL", ctypes.get_last_error(), flush=True)
    sys.exit(3)
import os
loop = os.path.join(os.path.dirname(os.path.abspath(__file__)), "loop.py")
cell = subprocess.Popen(f'"{sys.executable}" "{loop}" "{marker}"', shell=True)
print(f"CELL {cell.pid}", flush=True)
print("READY", flush=True)
time.sleep(120)
