#!/usr/bin/env python3

import sys
import time
from track import read_points
from telnet import TelenetConnection


tc = TelenetConnection(logfile=sys.stdout)
time.sleep(0.5)

points = read_points(sys.stdin)
assert points and points[0].time is not None

t = points[0].time.timestamp()

for p in points:
    assert p.time is not None

    pt = p.time.timestamp()
    time.sleep(pt - t)
    t = pt

    tc.write(f'geo fix {p.lon} {p.lat} {p.elevation} 9')


# with subprocess.Popen(
#     ['telnet', 'localhost', '5554'],
#     stdin=subprocess.PIPE,
#     stdout=subprocess.PIPE,
# ) as sp:
#     assert sp.stdin is not None and sp.stdout is not None
#
#     inp = sp.stdin
#     outp = sp.stdout
#
#     read_until_ok(outp)
#     time.sleep(0.5)
#
#     # auth
#     write(inp, "auth " + auth_token)
#     check_ok(outp, 1)
#     time.sleep(0.5)
#
#     points = read_points(sys.stdin)
#     assert points and points[0].time is not None
#
#     # writing geos
#     t = points[0].time.timestamp()
#
#     flag = False
#
#     for p in points:
#         assert p.time is not None
#
#         pt = p.time.timestamp()
#         time.sleep(pt - t)
#         t = pt
#
#         if flag:
#             write(inp, f'sensor set acceleration -1.53 9.69 0')
#         else:
#             write(inp, f'sensor set acceleration 20 20 0')
#
#         flag = not flag
#
#         write(inp, f'geo fix {p.lon} {p.lat} {p.elevation} 9')
