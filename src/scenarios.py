from __future__ import annotations

from math import sin

from src.config import SimulationConfig
from src.geometry import Panel


def build_conventional_scenario(config: SimulationConfig) -> list[Panel]:
    panels: list[Panel] = []
    grid_cols = max(config.num_panels // 2, 1)
    for idx in range(config.num_panels):
        row = idx // grid_cols
        col = idx % grid_cols
        x = col * config.base_spacing
        y = row * (config.base_spacing * 1.6)
        panels.append(
            Panel(
                panel_id=f"conv_{idx+1}",
                x=x,
                y=y,
                z=0.0,
                width=config.panel_width,
                height=config.panel_height,
                azimuth=90.0,
                tilt=90.0,
                level=0,
                scenario="Convencional",
            )
        )
    return panels


def build_bioinspired_scenario(config: SimulationConfig) -> list[Panel]:
    panels: list[Panel] = []
    for idx in range(config.num_panels):
        level = idx % config.num_levels
        col = idx // config.num_levels
        spacing = config.base_spacing * (0.85 + 0.12 * level)
        x = col * spacing + 0.45 * level
        y = level * (config.base_spacing * 1.15) + 0.35 * sin(idx)
        z = level * (config.panel_height * 0.55)
        azimuth = (60.0 + level * 25.0 + (idx % 3) * 10.0) % 360.0
        tilt = 78.0 + 4.0 * level
        width = config.panel_width * (0.92 + 0.05 * level)
        height = config.panel_height * (0.92 + 0.08 * level)
        panels.append(
            Panel(
                panel_id=f"bio_{idx+1}",
                x=x,
                y=y,
                z=z,
                width=width,
                height=height,
                azimuth=azimuth,
                tilt=min(tilt, 90.0),
                level=level,
                scenario="Bioinspirado",
            )
        )
    return panels


def build_bioinspired_variant(
    config: SimulationConfig,
    spacing_scale: float,
    height_scale: float,
    azimuth_shift: float,
) -> list[Panel]:
    variant = build_bioinspired_scenario(config)
    adjusted: list[Panel] = []
    for panel in variant:
        adjusted.append(
            Panel(
                panel_id=panel.panel_id,
                x=panel.x * spacing_scale,
                y=panel.y * spacing_scale,
                z=panel.z * height_scale,
                width=panel.width,
                height=panel.height * height_scale,
                azimuth=(panel.azimuth + azimuth_shift) % 360.0,
                tilt=panel.tilt,
                level=panel.level,
                scenario="Bioinspirado optimizado",
            )
        )
    return adjusted
