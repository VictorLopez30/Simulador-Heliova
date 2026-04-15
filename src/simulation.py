from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.config import LocationConfig, SimulationConfig
from src.geometry import Panel, panel_dataframe
from src.shading import aggregate_shading_losses, compute_shading_matrix
from src.solar_model import panel_incident_irradiance, solar_position_series


@dataclass(slots=True)
class ScenarioResult:
    name: str
    panels: list[Panel]
    panel_data: pd.DataFrame
    hourly_data: pd.DataFrame
    shading_map: pd.DataFrame
    panel_energy: pd.DataFrame


def simulate_scenario(
    name: str,
    panels: list[Panel],
    location: LocationConfig,
    config: SimulationConfig,
) -> ScenarioResult:
    solar_df = solar_position_series(location, config)
    hourly_records: list[dict] = []
    shading_records: list[dict] = []
    panel_energy_tracker: list[dict] = []

    for _, row in solar_df.iterrows():
        shading_df = compute_shading_matrix(
            panels,
            solar_elevation_deg=float(row["solar_elevation_deg"]),
            solar_azimuth_deg=float(row["solar_azimuth_deg"]),
            config=config,
        )
        shading_losses = aggregate_shading_losses(shading_df, [p.panel_id for p in panels])
        if not shading_df.empty:
            shading_df = shading_df.assign(hour=row["hour"])
            shading_records.extend(shading_df.to_dict("records"))

        total_energy_kwh = 0.0
        total_shading_loss_kwh = 0.0
        for panel in panels:
            irradiance = panel_incident_irradiance(
                panel=panel,
                solar_elevation_deg=float(row["solar_elevation_deg"]),
                solar_azimuth_deg=float(row["solar_azimuth_deg"]),
                dni=float(row["dni"]),
                dhi=float(row["dhi"]),
                albedo=config.albedo,
                bifacial_gain=config.bifacial_gain,
            )
            loss_fraction = shading_losses[panel.panel_id]
            effective_irradiance = irradiance * (1.0 - loss_fraction)
            hourly_energy_kwh = effective_irradiance * panel.area * config.module_efficiency / 1000.0
            lost_energy_kwh = irradiance * panel.area * config.module_efficiency / 1000.0 - hourly_energy_kwh
            total_energy_kwh += hourly_energy_kwh
            total_shading_loss_kwh += max(lost_energy_kwh, 0.0)
            panel_energy_tracker.append(
                {
                    "panel_id": panel.panel_id,
                    "scenario": name,
                    "hour": row["hour"],
                    "energy_kwh": hourly_energy_kwh,
                    "shading_loss_kwh": max(lost_energy_kwh, 0.0),
                    "loss_fraction": loss_fraction,
                }
            )

        hourly_records.append(
            {
                "scenario": name,
                "hour": row["hour"],
                "solar_elevation_deg": row["solar_elevation_deg"],
                "solar_azimuth_deg": row["solar_azimuth_deg"],
                "dni": row["dni"],
                "dhi": row["dhi"],
                "energy_kwh": total_energy_kwh,
                "shading_loss_kwh": total_shading_loss_kwh,
            }
        )

    panel_energy_df = pd.DataFrame(panel_energy_tracker)
    panel_summary = (
        panel_energy_df.groupby(["scenario", "panel_id"], as_index=False)[["energy_kwh", "shading_loss_kwh"]]
        .sum()
    )
    panel_summary = panel_summary.merge(panel_dataframe(panels), on="panel_id", how="left")
    return ScenarioResult(
        name=name,
        panels=panels,
        panel_data=panel_dataframe(panels),
        hourly_data=pd.DataFrame(hourly_records),
        shading_map=pd.DataFrame(shading_records),
        panel_energy=panel_summary,
    )


def export_result_data(result: ScenarioResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = result.name.lower().replace(" ", "_")
    result.hourly_data.to_csv(output_dir / f"{slug}_hourly.csv", index=False)
    result.panel_data.to_csv(output_dir / f"{slug}_panels.csv", index=False)
    result.panel_energy.to_csv(output_dir / f"{slug}_panel_energy.csv", index=False)
    if not result.shading_map.empty:
        result.shading_map.to_csv(output_dir / f"{slug}_shading.csv", index=False)
