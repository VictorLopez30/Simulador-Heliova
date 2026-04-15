from __future__ import annotations

from pathlib import Path

from src.main_engine import LOCATION_PRESETS, build_simulation_config, run_full_simulation


def main() -> None:
    config = build_simulation_config(
        num_panels=18,
        num_levels=3,
        spacing=3.0,
        height=2.2,
        diffuse_ratio=0.28,
    )
    result_bundle = run_full_simulation(
        config=config,
        location=LOCATION_PRESETS["Manaus, Brazil"],
        run_optimization=True,
        output_dir=Path("outputs"),
    )

    metrics_df = result_bundle["metrics_df"]
    print("Resumen de métricas:")
    print(metrics_df.round(3).to_string(index=False))
    print()
    print(result_bundle["conclusion"])
    print("Archivos generados en: outputs/")


if __name__ == "__main__":
    main()
