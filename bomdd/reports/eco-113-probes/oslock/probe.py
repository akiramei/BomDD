"""Probe msvcrt.locking semantics on this machine.

P1 a live holder blocks a non-blocking attempt.
P2 after the holder is killed (TerminateProcess), the lock can be taken.
P3 a child spawned by the holder (Popen defaults) does not keep the lock after the holder is killed.
P4 the same process cannot take the lock twice through a second fd (lock is per handle, not per process).
"""
import msvcrt
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def try_lock(path):
    fd = os.open(path, os.O_RDWR | os.O_CREAT)
    try:
        os.lseek(fd, 0, 0)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        return True
    except OSError:
        return False
    finally:
        os.close(fd)


def start(path, child=False):
    args = [sys.executable, os.path.join(HERE, "holder.py"), path] + (["child"] if child else [])
    p = subprocess.Popen(args, stdout=subprocess.PIPE, text=True)
    child_pid = None
    while True:
        line = p.stdout.readline().strip()
        if line.startswith("CHILD"):
            child_pid = int(line.split()[1])
        if line == "LOCKED":
            return p, child_pid


def wait_free(path, limit=5.0):
    t0 = time.time()
    while time.time() - t0 < limit:
        if try_lock(path):
            return round(time.time() - t0, 3)
        time.sleep(0.05)
    return None


d = tempfile.mkdtemp(prefix="oslock-")
lock = os.path.join(d, "ECO-999.lock")

p, _ = start(lock)
print("P1 live holder blocks:", not try_lock(lock))
p.kill(); p.wait()
print("P2 free after kill, seconds:", wait_free(lock))

p, cpid = start(lock, child=True)
print("P3 holder with child blocks:", not try_lock(lock))
p.kill(); p.wait()
print("P3 free after holder kill while child alive, seconds:", wait_free(lock))
subprocess.run(["taskkill", "/F", "/PID", str(cpid)], capture_output=True)

fd1 = os.open(lock, os.O_RDWR)
os.lseek(fd1, 0, 0)
msvcrt.locking(fd1, msvcrt.LK_NBLCK, 1)
print("P4 second fd in same process blocked:", not try_lock(lock))
msvcrt.locking(fd1, msvcrt.LK_UNLCK, 1)
os.close(fd1)
