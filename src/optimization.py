from __future__ import annotations

from src.config import LocationConfig, SimulationConfig
from src.metrics import compute_metrics
from src.scenarios import build_bioinspired_variant
from src.simulation import ScenarioResult, simulate_scenario


def optimize_bioinspired_layout(
    base_config: SimulationConfig,
    location: LocationConfig,
) -> tuple[ScenarioResult, dict[str, float]]:
    candidates = [
        {"spacing_scale": 0.9, "height_scale": 1.0, "azimuth_shift": -8.0},
        {"spacing_scale": 1.0, "height_scale": 1.05, "azimuth_shift": 0.0},
        {"spacing_scale": 1.1, "height_scale": 1.1, "azimuth_shift": 6.0},
        {"spacing_scale": 1.2, "height_scale": 1.0, "azimuth_shift": 12.0},
        {"spacing_scale": 0.95, "height_scale": 1.15, "azimuth_shift": -12.0},
    ]

    best_result: ScenarioResult | None = None
    best_metrics: dict[str, float] | None = None
    best_score = float("-inf")

    for candidate in candidates:
        panels = build_bioinspired_variant(base_config, **candidate)
        result = simulate_scenario("Bioinspirado optimizado", panels, location, base_config)
        metrics = compute_metrics(result, base_config)
        score = metrics["daily_energy_kwh"] + 2.5 * metrics["energy_per_m2_kwh"] - 0.7 * metrics["shading_loss_kwh"]
        if score > best_score:
            best_score = score
            best_result = result
            best_metrics = {**metrics, **candidate}

    assert best_result is not None
    assert best_metrics is not None
    return best_result, best_metrics
