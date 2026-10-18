import pathlib
import sys
import time

p = pathlib.Path(sys.argv[1])
i = 0
while True:
    i += 1
    p.write_text(str(i))
    time.sleep(0.2)
