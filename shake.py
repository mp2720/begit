#!/usr/bin/env python3

import time
import sys

from telnet import TelenetConnection

t = TelenetConnection(logfile=sys.stdout)

SHAKE_INTERVAL = 0.3

while True:
    time.sleep(SHAKE_INTERVAL)
    t.write('rotate')
    t.check_ok()
