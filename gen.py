from random import random
from datetime import datetime
from track import TrackPoint, read_points, write_points

import time
import sys


# углы
STEP = 1e-4
STEP_MAX_DISP = 1e-5
COORD_MAX_DISP = 2.5e-5
ELEV_MAX_DISP = 3

# км/ч
SPEED = 9
GLOBAL_SPEED_MAX_DISP = 0.5
LOCAL_SPEED_MAX_DISP = 3

START_TIME = "2024-11-28 18:57:01"

DIST_MAX_DISP = 5

DEGREES_IN_METER = 1.64e-5


def vlen(x: float, y: float) -> float: return (x**2 + y**2)**0.5


def dist(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    return vlen(lat1 - lat2, lon1 - lon2) / DEGREES_IN_METER


def disp(around: float, d: float) -> float:
    return around + d * (0.5 - random())


def gen_points(original: list[TrackPoint]) -> list[TrackPoint]:
    acc = 0

    def point_between(x1: float, y1: float, x2: float, y2: float, m: float) -> tuple[float, float]:
        dx, dy = x2 - x1, y2 - y1
        k = m / vlen(dx, dy)
        return (x1 + k * dx, y1 + k * dy)

    def points_between(a: TrackPoint, b: TrackPoint) -> list[TrackPoint]:
        nonlocal acc

        ret = []
        disp_from_a = -acc + disp(STEP, STEP_MAX_DISP)
        ab_len = vlen(a.lon - b.lon, a.lat - b.lat)
        while disp_from_a < ab_len:
            try:
                x, y = point_between(a.lon, a.lat, b.lon, b.lat, disp_from_a)
                x, y = disp(x, COORD_MAX_DISP), disp(
                    y, COORD_MAX_DISP)

                _, elevation = point_between(
                    0,
                    a.elevation,
                    ab_len,
                    b.elevation,
                    disp_from_a
                )
                elevation = disp(elevation, ELEV_MAX_DISP)

                ret.append(TrackPoint(
                    x,
                    y,
                    elevation
                ))
            except ZeroDivisionError:
                print("бывает", file=sys.stderr)

            disp_from_a += disp(STEP, STEP_MAX_DISP)

        acc = disp_from_a - ab_len

        return ret

    points = []
    for i in range(len(original) - 1):
        points += points_between(original[i], original[i + 1])

    return points


def calc_time(speed: float, start: float, points: list[TrackPoint]):
    points[0].time = datetime.fromtimestamp(start)
    t = start
    for i in range(1, len(points)):
        d = vlen(
            dist(
                points[i].lon,
                points[i].lat,
                points[i - 1].lon,
                points[i - 1].lat,
            ),
            points[i].elevation - points[i - 1].elevation
        )
        v = disp(speed, LOCAL_SPEED_MAX_DISP) / 3.6
        t += d / v
        points[i].time = datetime.fromtimestamp(t)


pts = read_points(sys.stdin)
pts = gen_points(pts)
calc_time(
    disp(SPEED - 1, GLOBAL_SPEED_MAX_DISP),
    time.mktime(
        datetime.strptime(
            START_TIME, "%Y-%m-%d %H:%M:%S"
        ).timetuple()
    ),
    pts
)
print(write_points(pts))
