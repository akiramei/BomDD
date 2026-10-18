"""Probe 2: the entry stays OUT of the job. It creates a kill-on-close job, starts the cell suspended (shell=True), assigns the cell's process to the
job through the process handle it holds, then resumes the cell's threads (Toolhelp thread snapshot filtered by that pid; the pid cannot be reused
while the handle is held).

K1 the entry is not in the new job; the job counts the shell and the command (ActiveProcesses == 2) and the command's counter advances.
K2 in-process normal end: when the cell exits and the entry closes its job handle, the job is gone (not found).
K3 the entry (a separate holder process doing the same) killed mid-cell → the command stops, the job is gone.
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
k32.CreateJobObjectW.restype = wt.HANDLE
k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wt.LPCWSTR]
k32.SetInformationJobObject.argtypes = [wt.HANDLE, ctypes.c_int, ctypes.c_void_p, wt.DWORD]
k32.AssignProcessToJobObject.argtypes = [wt.HANDLE, wt.HANDLE]
k32.OpenJobObjectW.restype = wt.HANDLE
k32.OpenJobObjectW.argtypes = [wt.DWORD, wt.BOOL, wt.LPCWSTR]
k32.QueryInformationJobObject.argtypes = [wt.HANDLE, ctypes.c_int, ctypes.c_void_p, wt.DWORD, ctypes.c_void_p]
k32.CloseHandle.argtypes = [wt.HANDLE]
k32.CreateToolhelp32Snapshot.restype = wt.HANDLE
k32.CreateToolhelp32Snapshot.argtypes = [wt.DWORD, wt.DWORD]
k32.OpenThread.restype = wt.HANDLE
k32.OpenThread.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
k32.ResumeThread.argtypes = [wt.HANDLE]
k32.IsProcessInJob.argtypes = [wt.HANDLE, wt.HANDLE, ctypes.POINTER(wt.BOOL)]
k32.GetCurrentProcess.restype = wt.HANDLE


class BASIC(ctypes.Structure):
    _fields_ = [("a", ctypes.c_int64), ("b", ctypes.c_int64), ("LimitFlags", wt.DWORD), ("c", ctypes.c_size_t), ("d", ctypes.c_size_t),
                ("e", wt.DWORD), ("f", ctypes.c_size_t), ("g", wt.DWORD), ("h", wt.DWORD)]


class EXT(ctypes.Structure):
    _fields_ = [("Basic", BASIC), ("Io", ctypes.c_uint64 * 6), ("i", ctypes.c_size_t), ("j", ctypes.c_size_t), ("k", ctypes.c_size_t),
                ("l", ctypes.c_size_t)]


class ACCT(ctypes.Structure):
    _fields_ = [("t", ctypes.c_int64 * 4), ("pf", wt.DWORD), ("TotalProcesses", wt.DWORD), ("ActiveProcesses", wt.DWORD), ("tt", wt.DWORD)]


class THREADENTRY32(ctypes.Structure):
    _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ThreadID", wt.DWORD), ("th32OwnerProcessID", wt.DWORD),
                ("tpBasePri", wt.LONG), ("tpDeltaPri", wt.LONG), ("dwFlags", wt.DWORD)]


k32.Thread32First.argtypes = [wt.HANDLE, ctypes.POINTER(THREADENTRY32)]
k32.Thread32Next.argtypes = [wt.HANDLE, ctypes.POINTER(THREADENTRY32)]


def launch_in_job(name, cmd):
    job = k32.CreateJobObjectW(None, name)
    ext = EXT()
    ext.Basic.LimitFlags = 0x2000
    assert k32.SetInformationJobObject(job, 9, ctypes.byref(ext), ctypes.sizeof(ext))
    p = subprocess.Popen(cmd, shell=True, creationflags=0x4)  # CREATE_SUSPENDED
    assert k32.AssignProcessToJobObject(job, int(p._handle)), ctypes.get_last_error()
    snap = k32.CreateToolhelp32Snapshot(0x4, 0)  # TH32CS_SNAPTHREAD
    te = THREADENTRY32()
    te.dwSize = ctypes.sizeof(te)
    resumed = 0
    ok = k32.Thread32First(snap, ctypes.byref(te))
    while ok:
        if te.th32OwnerProcessID == p.pid:
            th = k32.OpenThread(0x0002, False, te.th32ThreadID)  # THREAD_SUSPEND_RESUME
            k32.ResumeThread(th)
            k32.CloseHandle(th)
            resumed += 1
        ok = k32.Thread32Next(snap, ctypes.byref(te))
    k32.CloseHandle(snap)
    return job, p, resumed


def job_state(name):
    h = k32.OpenJobObjectW(0x0004, False, name)
    if not h:
        return ("gone", ctypes.get_last_error())
    a = ACCT()
    k32.QueryInformationJobObject(h, 1, ctypes.byref(a), ctypes.sizeof(a), None)
    k32.CloseHandle(h)
    return ("exists", a.ActiveProcesses)


def counter(marker):
    try:
        return open(marker).read()
    except OSError:
        return None


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "holder":
    job, p, n = launch_in_job(sys.argv[2], f'"{sys.executable}" "{os.path.join(HERE, "loop.py")}" "{sys.argv[3]}"')
    print("READY", n, flush=True)
    time.sleep(120)
    sys.exit(0)

d = tempfile.mkdtemp(prefix="jobprobe2-")
# K1 + K2: in-process
name = "Local\\BomDD-probe2-" + uuid.uuid4().hex[:10]
marker = os.path.join(d, "k1.txt")
short = os.path.join(d, "short.py")
open(short, "w").write("import pathlib,sys,time\nfor i in range(10):\n    pathlib.Path(sys.argv[1]).write_text(str(i)); time.sleep(0.2)\n")
job, p, n = launch_in_job(name, f'"{sys.executable}" "{short}" "{marker}"')
time.sleep(0.8)
inj = wt.BOOL()
k32.IsProcessInJob(k32.GetCurrentProcess(), job, ctypes.byref(inj))
print("K1 entry in the new job:", bool(inj.value), "| threads resumed:", n, "| job:", job_state(name), "| counter:", counter(marker))
p.wait()
print("   cell exit:", p.returncode, "| job before closing the entry's handle:", job_state(name))
k32.CloseHandle(job)
print("K2 job after the entry closed its handle:", job_state(name))
# K3: separate holder killed
name3 = "Local\\BomDD-probe2-" + uuid.uuid4().hex[:10]
m3 = os.path.join(d, "k3.txt")
h = subprocess.Popen([sys.executable, os.path.abspath(__file__), "holder", name3, m3], stdout=subprocess.PIPE, text=True)
print("   holder:", h.stdout.readline().strip())
time.sleep(1.0)
a = counter(m3); time.sleep(0.6); b = counter(m3)
print("   before kill: job", job_state(name3), "counter", a, "->", b)
h.kill(); h.wait(); time.sleep(1.5)
a = counter(m3); time.sleep(1.0); b = counter(m3)
print("K3 after the entry was killed: counter", a, "->", b, "(stopped)" if a == b else "(STILL ADVANCING)", "| job", job_state(name3))
