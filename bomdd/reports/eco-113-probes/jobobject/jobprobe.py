"""Probe: does a Job Object with KILL_ON_JOB_CLOSE give OS-managed ownership of a cell's whole process tree, without pids?

J1 the entry stand-in can create a named job and assign ITSELF to it here (this process may already be inside a job: nested).
J2 while it lives, the job can be opened by name and counts the entry, the shell and the grandchild (ActiveProcesses >= 3).
J3 killing the entry (TerminateProcess) ends the grandchild (the marker stops advancing).
J4 after that, opening the job by name fails with ERROR_FILE_NOT_FOUND (the job no longer exists).
"""
import ctypes
import ctypes.wintypes as wt
import os
import subprocess
import sys
import tempfile
import time
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenJobObjectW.restype = wt.HANDLE
k32.OpenJobObjectW.argtypes = [wt.DWORD, wt.BOOL, wt.LPCWSTR]
k32.QueryInformationJobObject.argtypes = [wt.HANDLE, ctypes.c_int, ctypes.c_void_p, wt.DWORD, ctypes.c_void_p]
k32.IsProcessInJob.argtypes = [wt.HANDLE, wt.HANDLE, ctypes.POINTER(wt.BOOL)]
k32.GetCurrentProcess.restype = wt.HANDLE
k32.CloseHandle.argtypes = [wt.HANDLE]


class ACCT(ctypes.Structure):
    _fields_ = [("TotalUserTime", ctypes.c_int64), ("TotalKernelTime", ctypes.c_int64), ("ThisPeriodTotalUserTime", ctypes.c_int64),
                ("ThisPeriodTotalKernelTime", ctypes.c_int64), ("TotalPageFaultCount", wt.DWORD), ("TotalProcesses", wt.DWORD),
                ("ActiveProcesses", wt.DWORD), ("TotalTerminatedProcesses", wt.DWORD)]


def open_job(name):
    h = k32.OpenJobObjectW(0x0004, False, name)  # JOB_OBJECT_QUERY
    if not h:
        return None, ctypes.get_last_error()
    a = ACCT()
    ok = k32.QueryInformationJobObject(h, 1, ctypes.byref(a), ctypes.sizeof(a), None)
    k32.CloseHandle(h)
    return (a.ActiveProcesses if ok else None), 0


inj = wt.BOOL()
k32.IsProcessInJob(k32.GetCurrentProcess(), None, ctypes.byref(inj))
print("driver already inside a job:", bool(inj.value))
name = "Local\\BomDD-probe-" + uuid.uuid4().hex[:12]
marker = os.path.join(tempfile.mkdtemp(prefix="jobprobe-"), "m.txt")
p = subprocess.Popen([sys.executable, os.path.join(HERE, "jobholder.py"), name, marker], stdout=subprocess.PIPE, text=True)
lines = []
while True:
    ln = p.stdout.readline().strip()
    lines.append(ln)
    if ln == "READY" or ln.endswith("_FAIL") or ln.startswith(("CREATE_FAIL", "SETINFO_FAIL", "ASSIGN_FAIL")) or not ln:
        break
print("J1 holder:", lines)
time.sleep(1.5)
print("J2 active processes while the entry lives:", open_job(name))
m1 = open(marker).read()
time.sleep(0.6)
m2 = open(marker).read()
print("   marker advancing before kill:", m1, "->", m2)
p.kill()
p.wait()
time.sleep(1.5)
a = open(marker).read()
time.sleep(1.0)
b = open(marker).read()
print("J3 marker after the entry was killed:", a, "->", b, "(stopped)" if a == b else "(STILL ADVANCING)")
print("J4 open job after kill (active, error):", open_job(name), "(2 = ERROR_FILE_NOT_FOUND)")
