from __future__ import annotations

from math import atan2, degrees

import numpy as np
import pandas as pd

from src.config import SimulationConfig
from src.geometry import Panel


def _angle_delta(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def compute_shading_matrix(
    panels: list[Panel],
    solar_elevation_deg: float,
    solar_azimuth_deg: float,
    config: SimulationConfig,
) -> pd.DataFrame:
    records: list[dict] = []
    if solar_elevation_deg <= 0:
        return pd.DataFrame(columns=["source", "target", "shade_factor"])

    elevation_rad = np.radians(solar_elevation_deg)
    shadow_scale = 1.0 / max(np.tan(elevation_rad), 0.12)

    for source in panels:
        for target in panels:
            if source.panel_id == target.panel_id:
                continue

            dx = target.x - source.x
            dy = target.y - source.y
            horizontal_distance = float(np.hypot(dx, dy))
            if horizontal_distance < 1e-6:
                continue

            source_to_target = (degrees(atan2(dx, dy)) + 360.0) % 360.0
            shadow_direction = (solar_azimuth_deg + 180.0) % 360.0
            angular_offset = _angle_delta(source_to_target, shadow_direction)
            if angular_offset > 40.0:
                continue

            shadow_length = max(source.height - 0.2 * max(target.level - source.level, 0), 0.4) * shadow_scale
            if horizontal_distance > shadow_length:
                continue

            lateral_tolerance = (source.width + target.width) * 0.7
            cross_track = horizontal_distance * np.sin(np.radians(angular_offset))
            if abs(cross_track) > lateral_tolerance:
                continue

            vertical_overlap = max((source.z + source.height) - target.z, 0.0)
            if vertical_overlap <= 0:
                continue

            distance_factor = 1.0 - (horizontal_distance / max(shadow_length, 1e-6))
            overlap_factor = min(vertical_overlap / max(target.height, 1e-6), 1.0)
            shade_factor = np.clip(
                config.shadow_decay * distance_factor * overlap_factor,
                0.0,
                0.95,
            )
            if shade_factor > 0:
                records.append(
                    {
                        "source": source.panel_id,
                        "target": target.panel_id,
                        "shade_factor": float(shade_factor),
                    }
                )

    return pd.DataFrame(records)


def aggregate_shading_losses(shading_df: pd.DataFrame, panel_ids: list[str]) -> dict[str, float]:
    losses = {panel_id: 0.0 for panel_id in panel_ids}
    if shading_df.empty:
        return losses

    grouped = shading_df.groupby("target")["shade_factor"].sum()
    for panel_id, value in grouped.items():
        losses[panel_id] = float(np.clip(value, 0.0, 0.98))
    return losses
