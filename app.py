from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src.main_engine import LOCATION_PRESETS, build_simulation_config, run_full_simulation


st.set_page_config(page_title="Simulación de Sistema Solar Bioinspirado", layout="wide")

st.title("Simulación de Sistema Solar Bioinspirado")
st.caption(
    "Prototipo computacional para comparar un sistema solar convencional vertical "
    "frente a una arquitectura multinivel bioinspirada en la canopia amazónica."
)

with st.sidebar:
    st.header("Parámetros")
    num_panels = st.slider("Número de paneles", min_value=6, max_value=48, value=18, step=2)
    num_levels = st.slider("Número de niveles", min_value=2, max_value=5, value=3, step=1)
    spacing = st.slider("Separación base (m)", min_value=1.5, max_value=6.0, value=3.0, step=0.1)
    height = st.slider("Altura de panel (m)", min_value=1.5, max_value=3.5, value=2.2, step=0.1)
    diffuse_ratio = st.slider("Proporción de radiación difusa", min_value=0.10, max_value=0.60, value=0.28, step=0.01)
    location_name = st.selectbox("Ubicación simplificada", options=list(LOCATION_PRESETS.keys()), index=0)
    run_optimization = st.toggle("Activar optimización", value=True)
    run_button = st.button("Ejecutar simulación", type="primary", use_container_width=True)


def render_metrics(metrics_map: dict[str, dict[str, float]], conclusion: str, comparison_best: dict[str, float]) -> None:
    scenarios = list(metrics_map.keys())
    cols = st.columns(min(3, len(scenarios)))
    for idx, scenario in enumerate(scenarios[: len(cols)]):
        metrics = metrics_map[scenario]
        with cols[idx]:
            st.metric("Escenario", scenario)
            st.metric("Energía diaria", f"{metrics['daily_energy_kwh']:.2f} kWh")
            st.metric("Energía por m²", f"{metrics['energy_per_m2_kwh']:.3f} kWh/m²")
            st.metric("Pérdidas por sombra", f"{metrics['shading_loss_kwh']:.2f} kWh")

    if len(scenarios) > len(cols):
        for scenario in scenarios[len(cols):]:
            metrics = metrics_map[scenario]
            st.write(
                f"**{scenario}**: {metrics['daily_energy_kwh']:.2f} kWh/día, "
                f"{metrics['energy_per_m2_kwh']:.3f} kWh/m², "
                f"pérdidas {metrics['shading_loss_kwh']:.2f} kWh"
            )

    st.success(conclusion)
    st.info(
        f"Mejora energética: {comparison_best['improvement_pct']:.1f}% | "
        f"Mejora por m²: {comparison_best['density_improvement_pct']:.1f}% | "
        f"Reducción de pérdidas por sombreado: {comparison_best['shading_reduction_pct']:.1f}%"
    )


def render_results(bundle: dict) -> None:
    st.subheader("Métricas principales")
    render_metrics(bundle["metrics_map"], bundle["conclusion"], bundle["comparison_best"])

    st.subheader("Comparación cuantitativa")
    st.dataframe(bundle["metrics_df"].round(3), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(bundle["figures"]["energy"], use_container_width=True)
    with col2:
        st.plotly_chart(bundle["figures"]["hourly"], use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.plotly_chart(bundle["figures"]["layout_2d"], use_container_width=True)
    with col4:
        st.plotly_chart(bundle["figures"]["shading"], use_container_width=True)

    st.subheader("Visualización 3D")
    st.plotly_chart(bundle["figures"]["layout_3d"], use_container_width=True)

    if bundle["optimized_meta"]:
        st.subheader("Parámetros seleccionados en la optimización")
        st.json(bundle["optimized_meta"])

    st.subheader("Archivos de salida")
    output_files = sorted(Path("outputs").glob("*"))
    st.write(pd.DataFrame({"archivo": [file.name for file in output_files]}))


if run_button:
    with st.spinner("Ejecutando simulación y generando visualizaciones..."):
        config = build_simulation_config(
            num_panels=num_panels,
            num_levels=num_levels,
            spacing=spacing,
            height=height,
            diffuse_ratio=diffuse_ratio,
        )
        bundle = run_full_simulation(
            config=config,
            location=LOCATION_PRESETS[location_name],
            run_optimization=run_optimization,
            output_dir=Path("outputs"),
        )
    render_results(bundle)
else:
    st.markdown(
        """
        ### Qué evalúa esta app
        - Energía total diaria y anual estimada.
        - Energía por metro cuadrado.
        - Pérdidas por sombreado entre paneles.
        - Mejora porcentual del arreglo bioinspirado respecto a un arreglo vertical uniforme.

        Usa el panel lateral para ajustar el sistema y ejecuta la simulación.
        """
    )
