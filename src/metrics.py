from __future__ import annotations

import pandas as pd

from src.config import SimulationConfig
from src.simulation import ScenarioResult


def compute_metrics(result: ScenarioResult, config: SimulationConfig) -> dict[str, float]:
    total_daily = float(result.hourly_data["energy_kwh"].sum())
    total_annual = total_daily * config.annualization_factor
    total_loss = float(result.hourly_data["shading_loss_kwh"].sum())
    total_area = float(result.panel_data["area"].sum())
    energy_per_m2 = total_daily / total_area if total_area else 0.0
    energy_per_panel = total_daily / len(result.panels) if result.panels else 0.0
    return {
        "daily_energy_kwh": total_daily,
        "annual_energy_kwh": total_annual,
        "shading_loss_kwh": total_loss,
        "energy_per_m2_kwh": energy_per_m2,
        "energy_per_panel_kwh": energy_per_panel,
        "total_area_m2": total_area,
        "panel_count": float(len(result.panels)),
    }


def compare_metrics(
    conventional_metrics: dict[str, float],
    bio_metrics: dict[str, float],
) -> dict[str, float]:
    base_daily = conventional_metrics["daily_energy_kwh"]
    base_density = conventional_metrics["energy_per_m2_kwh"]
    improvement = ((bio_metrics["daily_energy_kwh"] - base_daily) / base_daily * 100.0) if base_daily else 0.0
    density_improvement = ((bio_metrics["energy_per_m2_kwh"] - base_density) / base_density * 100.0) if base_density else 0.0
    shading_reduction = (
        (conventional_metrics["shading_loss_kwh"] - bio_metrics["shading_loss_kwh"])
        / conventional_metrics["shading_loss_kwh"]
        * 100.0
    ) if conventional_metrics["shading_loss_kwh"] else 0.0
    return {
        "improvement_pct": improvement,
        "density_improvement_pct": density_improvement,
        "shading_reduction_pct": shading_reduction,
    }


def metrics_table(metrics_map: dict[str, dict[str, float]]) -> pd.DataFrame:
    return pd.DataFrame(metrics_map).T.reset_index().rename(columns={"index": "scenario"})
