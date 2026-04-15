from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class LocationConfig:
    name: str = "Manaus, Brazil"
    latitude: float = -3.1
    longitude: float = -60.0
    timezone: str = "America/Manaus"


@dataclass(slots=True)
class SimulationConfig:
    num_panels: int = 18
    num_levels: int = 3
    base_spacing: float = 3.0
    panel_width: float = 1.1
    panel_height: float = 2.2
    start_hour: int = 6
    end_hour: int = 18
    day_of_year: int = 172
    dni_peak: float = 850.0
    dhi_peak: float = 220.0
    albedo: float = 0.18
    bifacial_gain: float = 0.12
    module_efficiency: float = 0.20
    diffuse_ratio: float = 0.28
    direct_ratio: float = 0.72
    shadow_decay: float = 0.65
    annualization_factor: int = 365
    outputs_dir: Path = field(default_factory=lambda: Path("outputs"))


DEFAULT_LOCATION = LocationConfig()
DEFAULT_SIMULATION = SimulationConfig()
