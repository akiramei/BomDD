import os, sys, time, subprocess, msvcrt, errno, tempfile

D = os.path.dirname(os.path.abspath(__file__))
LOCK = os.path.join(D, "probe.lock")

def try_lock():
    fd = os.open(LOCK, os.O_RDWR | os.O_CREAT)
    os.lseek(fd, 0, 0)
    try:
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        return fd, None
    except OSError as e:
        os.close(fd)
        return None, (e.errno, errno.errorcode.get(e.errno), getattr(e, "winerror", None))

if sys.argv[1:] == ["holder"]:
    fd, err = try_lock()
    print("holder locked", err, flush=True)
    mode = sys.argv[2] if len(sys.argv) > 2 else ""
    sys.stdout.flush()
    time.sleep(60)

elif len(sys.argv) > 1 and sys.argv[1] == "holder_inherit":
    fd, err = try_lock()
    os.set_inheritable(fd, True)
    # spawn a child that inherits the handle and sleeps
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"], close_fds=False)
    print("holder_inherit locked", err, "child", child.pid, flush=True)
    time.sleep(60)

elif len(sys.argv) > 1 and sys.argv[1] == "holder_default_child":
    fd, err = try_lock()
    child = subprocess.Popen("ping -n 30 127.0.0.1 >NUL", shell=True)
    print("holder_default_child locked", err, "child", child.pid, flush=True)
    time.sleep(60)

else:
    # main driver
    for kind in ["holder", "holder_default_child", "holder_inherit"]:
        p = subprocess.Popen([sys.executable, __file__, kind], stdout=subprocess.PIPE, text=True)
        line = p.stdout.readline().strip()
        print("started:", line)
        fd, err = try_lock()
        print(kind, "conflict while holder alive:", err)
        if fd is not None:
            os.close(fd)
        p.kill(); p.wait()
        t0 = time.time()
        got = None
        while time.time() - t0 < 5:
            fd, err = try_lock()
            if fd is not None:
                got = time.time() - t0
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                os.close(fd)
                break
            time.sleep(0.05)
        print(kind, "after kill: lock acquired after", got, "last err", err)
    # text mode probe
    tp = os.path.join(D, "tm.jsonl")
    if os.path.exists(tp): os.remove(tp)
    fd = os.open(tp, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
    n = os.write(fd, b'{"a":1}\n')
    os.close(fd)
    print("text-mode os.write returned", n, "bytes on disk", open(tp, "rb").read())
    # LK_LOCK conflict errno (blocking with retries)
    p = subprocess.Popen([sys.executable, __file__, "holder"], stdout=subprocess.PIPE, text=True)
    p.stdout.readline()
    fd = os.open(LOCK, os.O_RDWR | os.O_CREAT)
    t0 = time.time()
    try:
        msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
        print("LK_LOCK unexpectedly acquired")
    except OSError as e:
        print("LK_LOCK conflict:", e.errno, errno.errorcode.get(e.errno), "after", round(time.time()-t0,1))
    os.close(fd)
    # read the locked byte from another handle
    fd = os.open(LOCK, os.O_RDONLY)
    try:
        print("read locked byte:", os.read(fd, 1))
    except OSError as e:
        print("read locked byte err:", e)
    os.close(fd)
    # file size of lock
    print("lock file size", os.path.getsize(LOCK))
    p.kill(); p.wait()
