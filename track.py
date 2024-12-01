from dataclasses import dataclass
from datetime import datetime
import gpxpy.gpx


@dataclass
class TrackPoint:
    lon: float
    lat: float
    elevation: float
    time: datetime | None = None


def read_points(file) -> list[TrackPoint]:
    points = []

    gpx = gpxpy.parse(file)
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append(TrackPoint(
                    point.longitude,
                    point.latitude,
                    point.elevation,
                    point.time
                ))

    return points


def write_points(points: list[TrackPoint]) -> str:
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
