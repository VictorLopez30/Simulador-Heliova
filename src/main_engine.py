from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from src.config import DEFAULT_SIMULATION, LocationConfig, SimulationConfig
from src.metrics import compare_metrics, compute_metrics, metrics_table
from src.optimization import optimize_bioinspired_layout
from src.scenarios import build_bioinspired_scenario, build_conventional_scenario
from src.simulation import ScenarioResult, export_result_data, simulate_scenario
from src.visualization import (
    create_energy_comparison_figure,
    create_hourly_figure,
    create_layout_2d_figure,
    create_layout_3d_figure,
    create_shading_heatmap,
    save_plotly_figure,
    save_summary_matplotlib,
)


LOCATION_PRESETS: dict[str, LocationConfig] = {
    "Manaus, Brazil": LocationConfig(name="Manaus, Brazil", latitude=-3.1, longitude=-60.0, timezone="America/Manaus"),
    "Mexico City, Mexico": LocationConfig(name="Mexico City, Mexico", latitude=19.43, longitude=-99.13, timezone="America/Mexico_City"),
    "Bogota, Colombia": LocationConfig(name="Bogota, Colombia", latitude=4.71, longitude=-74.07, timezone="America/Bogota"),
    "Quito, Ecuador": LocationConfig(name="Quito, Ecuador", latitude=-0.18, longitude=-78.47, timezone="America/Guayaquil"),
}


def build_simulation_config(
    num_panels: int,
    num_levels: int,
    spacing: float,
    height: float,
    diffuse_ratio: float,
) -> SimulationConfig:
    direct_ratio = max(0.05, 1.0 - diffuse_ratio)
    return replace(
        DEFAULT_SIMULATION,
        num_panels=num_panels,
        num_levels=num_levels,
        base_spacing=spacing,
        panel_height=height,
        diffuse_ratio=diffuse_ratio,
        direct_ratio=direct_ratio,
    )


def run_full_simulation(
    config: SimulationConfig,
    location: LocationConfig,
    run_optimization: bool = False,
    output_dir: Path | None = None,
) -> dict:
    output_dir = output_dir or config.outputs_dir
    conventional = simulate_scenario("Convencional", build_conventional_scenario(config), location, config)
    bio_base = simulate_scenario("Bioinspirado", build_bioinspired_scenario(config), location, config)

    results: list[ScenarioResult] = [conventional, bio_base]
    metrics_map = {
        conventional.name: compute_metrics(conventional, config),
        bio_base.name: compute_metrics(bio_base, config),
    }

    optimized_meta: dict | None = None
    if run_optimization:
        bio_optimized, optimized_metrics = optimize_bioinspired_layout(config, location)
        results.append(bio_optimized)
        metrics_map[bio_optimized.name] = compute_metrics(bio_optimized, config)
        optimized_meta = optimized_metrics

    comparison = compare_metrics(metrics_map["Convencional"], metrics_map["Bioinspirado"])
    reference_bio_name = "Bioinspirado optimizado" if "Bioinspirado optimizado" in metrics_map else "Bioinspirado"
    comparison_best = compare_metrics(metrics_map["Convencional"], metrics_map[reference_bio_name])

    for result in results:
        export_result_data(result, output_dir)

    metrics_df = metrics_table(metrics_map)
    energy_fig = create_energy_comparison_figure(metrics_df)
    hourly_fig = create_hourly_figure(results)
    layout_2d_fig = create_layout_2d_figure(bio_base)
    layout_3d_fig = create_layout_3d_figure(results[-1] if run_optimization else bio_base)
    shading_fig = create_shading_heatmap(results[-1] if run_optimization else bio_base)

    save_plotly_figure(energy_fig, output_dir / "energy_comparison.html")
    save_plotly_figure(hourly_fig, output_dir / "hourly_profile.html")
    save_plotly_figure(layout_2d_fig, output_dir / "layout_2d.html")
    save_plotly_figure(layout_3d_fig, output_dir / "layout_3d.html")
    save_plotly_figure(shading_fig, output_dir / "shading_map.html")
    save_summary_matplotlib(metrics_df, output_dir / "energy_density.png")
    metrics_df.to_csv(output_dir / "summary_metrics.csv", index=False)

    conclusion = (
        f"El sistema bioinspirado mejora {comparison_best['improvement_pct']:.1f}% "
        f"respecto al convencional en energía diaria."
    )

    return {
        "config": config,
        "location": location,
        "results": results,
        "metrics_map": metrics_map,
        "metrics_df": metrics_df,
        "comparison_base": comparison,
        "comparison_best": comparison_best,
        "optimized_meta": optimized_meta,
        "figures": {
            "energy": energy_fig,
            "hourly": hourly_fig,
            "layout_2d": layout_2d_fig,
            "layout_3d": layout_3d_fig,
            "shading": shading_fig,
        },
        "conclusion": conclusion,
    }
