import math
from random import random
import time
from datetime import datetime
import gpxpy.gpx
import sys

from dataclasses import dataclass


@dataclass
class TrackPoint:
    lon: float
    lat: float
    elevation: float
    time: datetime | None = None


# км
EARTH_RADIUS = 6371e3

# углы
STEP = 1e-4
STEP_MAX_DISP = 1e-5
COORD_MAX_DISP = 2.5e-5
ELEV_MAX_DISP = 3

# км/ч
SPEED = 8
GLOBAL_SPEED_MAX_DISP = 0.5
LOCAL_SPEED_MAX_DISP = 0.15

START_TIME = "2024-11-28 18:57:01"


def dist(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    phi1 = lat1 * math.pi / 180
    phi2 = lat2 * math.pi / 180
    delta_lambda = (lon1 - lon2) * math.pi / 180
    d = math.acos(math.sin(phi1) * math.sin(phi2) + math.cos(phi1)
                  * math.cos(phi2) * math.cos(delta_lambda)) * EARTH_RADIUS
    return d


def read_points(file) -> list[TrackPoint]:
    points = []

    gpx = gpxpy.parse(file)
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(TrackPoint(
                    point.longitude,
                    point.latitude,
                    point.elevation
                ))

    return points


def disp(around: float, d: float) -> float:
    return around + d * (0.5 - random())


def gen_points(original: list[TrackPoint]) -> list[TrackPoint]:
    acc = 0

    def vlen(x: float, y: float) -> float: return (x**2 + y**2)**0.5

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
        d = dist(
            points[i].lon,
            points[i].lat,
            points[i - 1].lon,
            points[i - 1].lat,
        )
        v = disp(speed, LOCAL_SPEED_MAX_DISP) / 3.6
        t += d / v
        points[i].time = datetime.fromtimestamp(t)


def gen_gpx(points: list[TrackPoint]) -> str:
    gpx = gpxpy.gpx.GPX()

    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    for p in points:
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(
            p.lat,
            p.lon,
            elevation=p.elevation,
            time=p.time
        ))

    return gpx.to_xml()


pts = read_points(sys.stdin)
pts = gen_points(pts)
calc_time(
    disp(SPEED, GLOBAL_SPEED_MAX_DISP),
    time.mktime(
        datetime.strptime(
            START_TIME, "%Y-%m-%d %H:%M:%S"
        ).timetuple()
    ),
    pts
)
print(gen_gpx(pts))
