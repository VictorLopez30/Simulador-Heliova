from __future__ import annotations

from math import cos, pi, radians, sin

import numpy as np
import pandas as pd

from src.config import LocationConfig, SimulationConfig
from src.geometry import Panel


def solar_position_series(location: LocationConfig, config: SimulationConfig) -> pd.DataFrame:
    hours = np.arange(config.start_hour, config.end_hour + 1, dtype=float)
    lat = radians(location.latitude)
    decl = radians(23.45 * sin(2 * pi * (284 + config.day_of_year) / 365))
    solar_time = hours - 12.0
    hour_angle = np.radians(15.0 * solar_time)

    elevation = np.arcsin(
        np.sin(lat) * np.sin(decl) + np.cos(lat) * np.cos(decl) * np.cos(hour_angle)
    )
    elevation_deg = np.degrees(np.clip(elevation, 0.0, None))
    azimuth = np.degrees(
        np.arctan2(
            np.sin(hour_angle),
            np.cos(hour_angle) * np.sin(lat) - np.tan(decl) * np.cos(lat),
        )
    )
    azimuth = (azimuth + 180.0) % 360.0
    daylight_factor = np.clip(np.sin(np.radians(elevation_deg)), 0.0, None)
    dni = config.dni_peak * daylight_factor * config.direct_ratio
    dhi = config.dhi_peak * np.sqrt(daylight_factor) * config.diffuse_ratio

    return pd.DataFrame(
        {
            "hour": hours,
            "solar_elevation_deg": elevation_deg,
            "solar_azimuth_deg": azimuth,
            "dni": dni,
            "dhi": dhi,
        }
    )


def sun_vector(elevation_deg: float, azimuth_deg: float) -> np.ndarray:
    el = radians(elevation_deg)
    az = radians(azimuth_deg)
    return np.array([cos(el) * sin(az), cos(el) * cos(az), sin(el)], dtype=float)


def panel_incident_irradiance(
    panel: Panel,
    solar_elevation_deg: float,
    solar_azimuth_deg: float,
    dni: float,
    dhi: float,
    albedo: float,
    bifacial_gain: float,
) -> float:
    if solar_elevation_deg <= 0:
        return 0.0

    sun = sun_vector(solar_elevation_deg, solar_azimuth_deg)
    front_cos = float(np.clip(np.dot(panel.normal_vector, sun), 0.0, 1.0))
    rear_cos = float(np.clip(np.dot(-panel.normal_vector, sun), 0.0, 1.0))
    sky_view = 0.5 * (1.0 + np.cos(np.radians(panel.tilt)))

    direct_component = dni * (front_cos + bifacial_gain * rear_cos)
    diffuse_component = dhi * sky_view
    reflected_component = (dni * np.sin(np.radians(solar_elevation_deg)) + dhi) * albedo * 0.5
    return max(direct_component + diffuse_component + reflected_component, 0.0)
