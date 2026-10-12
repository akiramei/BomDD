"""Timing probe loaded by every Python the measured hook starts (PYTHONPATH points here).

Appends one JSON line per process start, per subprocess.run call (check_output goes through it)
and per process exit to the file named by GATE_TIMER_LOG. Every write is wrapped so that the probe
can never change what the measured code does or returns; without GATE_TIMER_LOG it does nothing.
"""
import os

_LOG = os.environ.get("GATE_TIMER_LOG")

if _LOG:
    import atexit
    import json
    import subprocess
    import sys
    import time

    def _write(record):
        try:
            record["pid"] = os.getpid()
            record["ppid"] = os.getppid()
            with open(_LOG, "a", encoding="utf-8") as handle:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _argv(value):
        try:
            if isinstance(value, (list, tuple)):
                return [str(item) for item in value][:8]
            return [str(value)]
        except Exception:
            return ["?"]

    _write({"event": "start", "t": time.time(), "argv": _argv(sys.argv), "cwd": os.getcwd()})
    atexit.register(lambda: _write({"event": "exit", "t": time.time(), "argv": _argv(sys.argv)}))

    _original_run = subprocess.run

    def _timed_run(*args, **kwargs):
        started = time.time()
        returncode = None
        try:
            result = _original_run(*args, **kwargs)
            returncode = getattr(result, "returncode", None)
            return result
        except subprocess.CalledProcessError as error:
            returncode = error.returncode
            raise
        finally:
            command = args[0] if args else kwargs.get("args")
            _write({
                "event": "run",
                "t": started,
                "dt": time.time() - started,
                "argv": _argv(command),
                "cwd": str(kwargs.get("cwd") or ""),
                "rc": returncode,
            })

    subprocess.run = _timed_run
