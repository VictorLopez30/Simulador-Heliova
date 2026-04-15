from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go

from src.simulation import ScenarioResult


def create_energy_comparison_figure(metrics_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_bar(
        x=metrics_df["scenario"],
        y=metrics_df["daily_energy_kwh"],
        name="Energía diaria",
        marker_color=["#456990", "#2A9D8F", "#E9C46A"][: len(metrics_df)],
    )
    fig.update_layout(
        title="Comparación de energía diaria",
        xaxis_title="Escenario",
        yaxis_title="kWh/día",
        template="plotly_white",
    )
    return fig


def create_hourly_figure(results: list[ScenarioResult]) -> go.Figure:
    fig = go.Figure()
    palette = ["#1D3557", "#2A9D8F", "#F4A261"]
    for idx, result in enumerate(results):
        fig.add_scatter(
            x=result.hourly_data["hour"],
            y=result.hourly_data["energy_kwh"],
            mode="lines+markers",
            name=result.name,
            line=dict(color=palette[idx % len(palette)], width=3),
        )
    fig.update_layout(
        title="Producción horaria",
        xaxis_title="Hora solar",
        yaxis_title="kWh",
        template="plotly_white",
    )
    return fig


def create_layout_2d_figure(result: ScenarioResult) -> go.Figure:
    df = result.panel_data.copy()
    fig = go.Figure()
    fig.add_scatter(
        x=df["x"],
        y=df["y"],
        mode="markers+text",
        text=df["level"].astype(str),
        textposition="top center",
        marker=dict(
            size=14,
            color=df["level"],
            colorscale="Viridis",
            line=dict(width=1, color="#264653"),
        ),
        name=result.name,
    )
    fig.update_layout(
        title=f"Vista 2D del arreglo: {result.name}",
        xaxis_title="X (m)",
        yaxis_title="Y (m)",
        template="plotly_white",
    )
    return fig


def create_layout_3d_figure(result: ScenarioResult) -> go.Figure:
    df = result.panel_data.copy()
    fig = go.Figure(
        data=[
            go.Scatter3d(
                x=df["x"],
                y=df["y"],
                z=df["z"] + df["height"] / 2.0,
                mode="markers",
                marker=dict(size=7, color=df["level"], colorscale="Viridis", opacity=0.9),
                text=[
                    f"{row.panel_id}<br>Nivel {row.level}<br>Az {row.azimuth:.0f}°"
                    for row in df.itertuples()
                ],
                name=result.name,
            )
        ]
    )
    fig.update_layout(
        title=f"Vista 3D del sistema: {result.name}",
        scene=dict(xaxis_title="X (m)", yaxis_title="Y (m)", zaxis_title="Z (m)"),
        template="plotly_white",
    )
    return fig


def create_shading_heatmap(result: ScenarioResult) -> go.Figure:
    if result.shading_map.empty:
        fig = go.Figure()
        fig.update_layout(
            title=f"Mapa de sombreado: {result.name}",
            template="plotly_white",
            annotations=[
                dict(
                    text="Sin pérdidas de sombreado detectables en la jornada simulada",
                    x=0.5,
                    y=0.5,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                )
            ],
        )
        return fig

    heatmap_df = (
        result.shading_map.groupby(["source", "target"], as_index=False)["shade_factor"].mean()
        .pivot(index="source", columns="target", values="shade_factor")
        .fillna(0.0)
    )
    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_df.values,
            x=list(heatmap_df.columns),
            y=list(heatmap_df.index),
            colorscale="YlOrRd",
        )
    )
    fig.update_layout(
        title=f"Mapa simple de sombreado: {result.name}",
        xaxis_title="Panel sombreado",
        yaxis_title="Panel fuente",
        template="plotly_white",
    )
    return fig


def save_plotly_figure(fig: go.Figure, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path), include_plotlyjs="cdn")


def save_summary_matplotlib(metrics_df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 5))
    plt.bar(
        metrics_df["scenario"],
        metrics_df["energy_per_m2_kwh"],
        color=["#577590", "#43AA8B", "#F9C74F"][: len(metrics_df)],
    )
    plt.ylabel("kWh/m² por día")
    plt.title("Densidad energética por escenario")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
