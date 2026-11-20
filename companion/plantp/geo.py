"""Geographic coordinates on a spherical Earth, chapter 3 (used in chapters 13, 14 and 29).

    haversine_m       great-circle distance between two points (metres)
    bearing_deg       initial bearing from point 1 to point 2, degrees clockwise from north
    enu_offsets_m     local east/north offsets from a reference point (flat-Earth patch)

Latitude and longitude in decimal degrees (north and east positive). The sphere has the
mean Earth radius; real surveying uses an ellipsoid and a projected grid (chapter 29).
"""
from __future__ import annotations

import math

import numpy as np

R_EARTH_M = 6_371_008.8     # mean Earth radius


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = p2 - p1
    dl = np.radians(np.asarray(lon2, dtype=float) - np.asarray(lon1, dtype=float))
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R_EARTH_M * np.arcsin(np.sqrt(a))


def bearing_deg(lat1, lon1, lat2, lon2) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    x = math.sin(dl) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dl)
    return math.degrees(math.atan2(x, y)) % 360.0


def enu_offsets_m(lat0, lon0, lat, lon):
    """East and north offsets (m) of (lat, lon) from (lat0, lon0) on a local flat patch."""
    east = R_EARTH_M * np.radians(np.asarray(lon, dtype=float) - lon0) * math.cos(math.radians(lat0))
    north = R_EARTH_M * np.radians(np.asarray(lat, dtype=float) - lat0)
    return east, north
