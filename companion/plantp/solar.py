"""Sun position and angle of incidence: a trigonometry application (chapter 3; the
full solar-resource treatment is chapter 12).

Textbook formulas (Cooper's declination, Spencer's equation of time), accurate to
roughly a degree and a minute or two - enough for teaching and screening, not for
tracker control. Angles in degrees at the interface. Azimuth follows the Plant P
convention (A-023): from true north, clockwise.

Plant P: latitude 34 deg N; clock time UTC+04:00 whose zone meridian (60 deg E) is
taken as the site meridian (A-003), so solar time = clock time + equation of time.
"""
from __future__ import annotations

import math

import numpy as np


def declination(day_of_year):
    """Solar declination in degrees (Cooper): 23.45 sin(360 (284 + n) / 365)."""
    n = np.asarray(day_of_year, dtype=float)
    return 23.45 * np.sin(np.radians(360.0 * (284.0 + n) / 365.0))


def equation_of_time(day_of_year):
    """Equation of time in minutes (Spencer): apparent solar time - mean solar time."""
    b = np.radians((np.asarray(day_of_year, dtype=float) - 1.0) * 360.0 / 365.0)
    return 229.18 * (0.000075 + 0.001868 * np.cos(b) - 0.032077 * np.sin(b)
                     - 0.014615 * np.cos(2 * b) - 0.040849 * np.sin(2 * b))


def hour_angle(solar_time_h):
    """Hour angle in degrees: 15 deg per hour from solar noon, negative in the morning."""
    return 15.0 * (np.asarray(solar_time_h, dtype=float) - 12.0)


def solar_time(clock_h, day_of_year, longitude_deg: float = 60.0,
               zone_meridian_deg: float = 60.0):
    """Apparent solar time in hours from standard clock time."""
    return (np.asarray(clock_h, dtype=float) + 4.0 * (longitude_deg - zone_meridian_deg) / 60.0
            + equation_of_time(day_of_year) / 60.0)


def sun_position(latitude_deg: float, day_of_year, solar_time_h):
    """(elevation, azimuth) in degrees; azimuth from north, clockwise."""
    phi = math.radians(latitude_deg)
    d = np.radians(declination(day_of_year))
    w = np.radians(hour_angle(solar_time_h))
    sin_el = np.sin(phi) * np.sin(d) + np.cos(phi) * np.cos(d) * np.cos(w)
    el = np.arcsin(np.clip(sin_el, -1, 1))
    cos_az = (np.sin(d) - np.sin(el) * np.sin(phi)) / (np.cos(el) * np.cos(phi))
    az = np.degrees(np.arccos(np.clip(cos_az, -1, 1)))
    az = np.where(np.asarray(w) > 0, 360.0 - az, az)
    return np.degrees(el), az


def sunrise_hour_angle(latitude_deg: float, day_of_year):
    """Hour angle of sunrise in degrees (negative); day length = 2|w_s|/15 hours."""
    phi = math.radians(latitude_deg)
    d = np.radians(declination(day_of_year))
    return -np.degrees(np.arccos(np.clip(-np.tan(phi) * np.tan(d), -1, 1)))


def incidence_cos(elevation_deg, azimuth_deg, tilt_deg: float, surface_azimuth_deg: float):
    """cos of the angle between the sun and the normal of a tilted surface
    (dot product of two unit vectors); negative means the sun is behind the surface."""
    el = np.radians(elevation_deg)
    az = np.radians(azimuth_deg)
    b = math.radians(tilt_deg)
    g = math.radians(surface_azimuth_deg)
    return np.sin(el) * np.cos(b) + np.cos(el) * np.sin(b) * np.cos(az - g)


def sun_vector(elevation_deg, azimuth_deg):
    """Unit vector towards the sun in east-north-up coordinates."""
    el = np.radians(elevation_deg)
    az = np.radians(azimuth_deg)
    return np.array([np.cos(el) * np.sin(az), np.cos(el) * np.cos(az), np.sin(el)])


def surface_normal(tilt_deg: float, surface_azimuth_deg: float):
    """Unit normal of a surface tilted tilt_deg, facing surface_azimuth_deg (ENU)."""
    b = math.radians(tilt_deg)
    g = math.radians(surface_azimuth_deg)
    return np.array([math.sin(b) * math.sin(g), math.sin(b) * math.cos(g), math.cos(b)])
