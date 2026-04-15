from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin
from typing import Iterable

import numpy as np


@dataclass(slots=True)
class Panel:
    panel_id: str
    x: float
    y: float
    z: float
    width: float
    height: float
    azimuth: float
    tilt: float
    level: int
    scenario: str

    @property
    def area(self) -> float:
        return self.width * self.height

    @property
    def center(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z + self.height / 2.0], dtype=float)

    @property
    def normal_vector(self) -> np.ndarray:
        az = radians(self.azimuth)
        tilt = radians(self.tilt)
        horizontal = sin(tilt)
        return np.array(
            [horizontal * sin(az), horizontal * cos(az), cos(tilt)],
            dtype=float,
        )


def panel_dataframe(panels: Iterable[Panel]):
    import pandas as pd

    return pd.DataFrame(
        [
            {
                "panel_id": p.panel_id,
                "x": p.x,
                "y": p.y,
                "z": p.z,
                "width": p.width,
                "height": p.height,
                "azimuth": p.azimuth,
                "tilt": p.tilt,
                "level": p.level,
                "scenario": p.scenario,
                "area": p.area,
            }
            for p in panels
        ]
    )
