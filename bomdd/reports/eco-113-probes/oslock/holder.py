"""Take an OS lock on byte 0 of PATH and hold it. Optionally spawn a child that sleeps (to test non-inheritance)."""
import msvcrt
import os
import subprocess
import sys
import time

path = sys.argv[1]
spawn_child = len(sys.argv) > 2 and sys.argv[2] == "child"
fd = os.open(path, os.O_RDWR | os.O_CREAT)
os.lseek(fd, 0, 0)
msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
if spawn_child:
    c = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    print(f"CHILD {c.pid}", flush=True)
print("LOCKED", flush=True)
time.sleep(60)
