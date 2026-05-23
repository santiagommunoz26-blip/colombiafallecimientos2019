"""
pages.py
--------
Una función de renderizado por cada página de la aplicación:

- ``page_general``   → KPIs resumen + gráficos de tendencia, sexo y edad.
- ``page_territorio``→ Mapa coroplético + ranking de departamentos.
- ``page_causas``    → Top 15 causas CIE-10 + capítulos.
- ``page_demografia``→ Pirámide poblacional + estado civil + nivel educativo.

Todas reciben el DataFrame ya filtrado (``fdf``) y,
las que necesitan mapa, también reciben ``geo`` y ``GEO_ID``.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from modules.config import (
    BG_PRIMARY, ACCENT_PRIMARY, ACCENT_SECONDARY, ACCENT_TERTIARY,
    TEXT_SECONDARY, TEXT_MUTED, BORDER_COLOR,
    PLOTLY_LAYOUT, MESES_ORD, EDAD_ORDER,
    ESTADO_CIVIL_MAP, NIVEL_EDUCATIVO_MAP,
)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS INTERNOS
# ─────────────────────────────────────────────────────────────────────────────

def _sec(title: str) -> None:
    """Imprime un subtítulo de sección con el estilo definido en CSS."""
    st.markdown(f'<div class="sec-title">{title}</div>', unsafe_allow_html=True)


def _kpi_html(label: str, value: int, sub: str, main: bool = False) -> str:
    """Genera el HTML de una tarjeta KPI."""
    cls     = "kpi-card main-kpi" if main else "kpi-card"
    val_cls = "kpi-value"         if main else "kpi-value secondary"
    return f"""
    <div class="{cls}">
        <div class="kpi-label">{label}</div>
        <div class="{val_cls}">{value:,}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA GENERAL
# ─────────────────────────────────────────────────────────────────────────────

def page_general(fdf: pd.DataFrame) -> None:
    """
    Vista General: indicadores clave y distribuciones principales.

    Secciones
    ---------
    1. KPIs: total, natural, homicidio, suicidio, accidente.
    2. Manera de muerte (barras horizontales) + Tendencia mensual (líneas).
    3. Distribución por sexo (dona) + Muertes por grupo de edad (barras).
    """
    N = len(fdf)

    def _count(valor: str) -> int:
        return len(fdf[fdf["MANERA_MUERTE"] == valor]) if valor in fdf["MANERA_MUERTE"].values else 0

    nat, hom, suc, acc = _count("Natural"), _count("Homicidio"), _count("Suicidio"), _count("Accidente")
    pct = lambda v: f"{v/N*100:.1f}%" if N > 0 else "0%"

    kpi_data = [
        ("Total Muertes", N,   "Defunciones 2019", True),
        ("Natural",       nat, pct(nat),            False),
        ("Homicidios",    hom, pct(hom),            False),
        ("Suicidios",     suc, pct(suc),            False),
        ("Accidentes",    acc, pct(acc),            False),
    ]
    for col, (label, val, sub, main) in zip(st.columns(5), kpi_data):
        with col:
            st.markdown(_kpi_html(label, val, sub, main), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Manera de muerte + Tendencia mensual ─────────────────────────────
    col_left, col_right = st.columns([1, 1.6])

    with col_left:
        _sec("Manera de Muerte")
        manera_df = fdf["MANERA_MUERTE"].value_counts().reset_index()
        manera_df.columns = ["Manera", "Cantidad"]
        manera_df = manera_df.sort_values("Cantidad")

        n = len(manera_df)
        colors = [ACCENT_PRIMARY if i == n - 1 else ACCENT_TERTIARY for i in range(n)]

        fig = go.Figure(go.Bar(
            x=manera_df["Cantidad"], y=manera_df["Manera"], orientation="h",
            marker_color=colors,
            text=manera_df["Cantidad"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Muertes: %{x:,}<extra></extra>",
        ))
        fig.update_layout(
            **PLOTLY_LAYOUT, height=280,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        _sec("Tendencia Mensual")
        mes_df = (
            fdf.groupby(["MES", "MES_L", "MANERA_MUERTE"])
            .size().reset_index(name="n")
        )
        # Completar meses faltantes con 0 para evitar conexiones incorrectas
        maneras = mes_df["MANERA_MUERTE"].unique()
        idx = pd.MultiIndex.from_product(
            [range(1, 13), maneras], names=["MES", "MANERA_MUERTE"]
        )
        mes_df = mes_df.set_index(["MES", "MANERA_MUERTE"])["n"].reindex(idx, fill_value=0).reset_index()
        mes_df["MES_L"] = mes_df["MES"].map({i+1: m for i, m in enumerate(MESES_ORD)})
        mes_df["MES_L"] = pd.Categorical(mes_df["MES_L"], categories=MESES_ORD, ordered=True)
        mes_df = mes_df.sort_values("MES")

        fig2 = px.line(
            mes_df, x="MES_L", y="n", color="MANERA_MUERTE", markers=True,
            color_discrete_sequence=[ACCENT_PRIMARY, ACCENT_SECONDARY, ACCENT_TERTIARY,
                                     "#2563eb", "#1d4ed8"],
            labels={"n": "Muertes", "MES_L": "", "MANERA_MUERTE": ""},
        )
        fig2.update_traces(line_width=2, marker_size=5)
        fig2.update_layout(
            **PLOTLY_LAYOUT, height=280,
            legend=dict(orientation="h", yanchor="bottom", y=-0.35),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Sexo + Grupo de edad ─────────────────────────────────────────────
    col_sex, col_age = st.columns([1, 2])

    with col_sex:
        _sec("Distribución por Sexo")
        sex_df = (
            fdf[fdf["SEXO_L"].isin(["Masculino", "Femenino"])]
            ["SEXO_L"].value_counts().reset_index()
        )
        sex_df.columns = ["Sexo", "Cantidad"]
        max_pct = f"{sex_df['Cantidad'].max() / sex_df['Cantidad'].sum() * 100:.0f}%"

        fig3 = go.Figure(go.Pie(
            labels=sex_df["Sexo"], values=sex_df["Cantidad"], hole=0.6,
            marker_colors=[ACCENT_PRIMARY, ACCENT_SECONDARY],
            hovertemplate="<b>%{label}</b><br>Cantidad: %{value:,}<br>%{percent:.1%}<extra></extra>",
        ))
        fig3.update_layout(
            **PLOTLY_LAYOUT, height=240,
            annotations=[dict(text=max_pct, x=0.5, y=0.5, font_size=18,
                              showarrow=False, font_color=ACCENT_PRIMARY)],
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col_age:
        _sec("Muertes por Grupo de Edad")
        age_df = fdf["EDAD_L"].value_counts().reset_index()
        age_df.columns = ["Edad", "Cantidad"]
        age_df["Edad"] = pd.Categorical(age_df["Edad"], categories=EDAD_ORDER, ordered=True)
        age_df = age_df.dropna().sort_values("Edad")

        fig4 = go.Figure(go.Bar(
            x=age_df["Edad"], y=age_df["Cantidad"],
            marker=dict(
                color=age_df["Cantidad"],
                colorscale=[[0, BG_PRIMARY], [0.5, ACCENT_PRIMARY], [1, ACCENT_SECONDARY]],
                showscale=False,
            ),
            hovertemplate="<b>%{x}</b><br>Muertes: %{y:,}<extra></extra>",
        ))
        fig4.update_layout(
            **PLOTLY_LAYOUT, height=240,
            xaxis=dict(tickangle=-45, tickfont=dict(size=9)),
            yaxis=dict(gridcolor=BORDER_COLOR),
        )
        st.plotly_chart(fig4, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA TERRITORIO
# ─────────────────────────────────────────────────────────────────────────────

def page_territorio(fdf: pd.DataFrame, geo: dict, GEO_ID: str) -> None:
    """
    Vista Territorio: distribución geográfica de la mortalidad.

    Secciones
    ---------
    1. Mapa coroplético por departamento (Plotly choropleth + GeoJSON).
    2. Top 10 departamentos con mayor mortalidad (barras horizontales).
    """
    col_map, col_rank = st.columns([1.7, 1])

    with col_map:
        _sec("Mapa de Mortalidad por Departamento")
        map_df = fdf.groupby(["COD_DEPARTAMENTO", "DEPARTAMENTO"]).size().reset_index(name="total")
        map_df["COD_STR"] = map_df["COD_DEPARTAMENTO"].astype(str).str.zfill(2)

        fig_map = px.choropleth(
            map_df, geojson=geo,
            locations="COD_STR", featureidkey=f"properties.{GEO_ID}",
            color="total", hover_name="DEPARTAMENTO",
            hover_data={"total": ":,.0f"},
            color_continuous_scale=[
                [0,   BG_PRIMARY],
                [0.3, "#1e3a8a"],
                [0.6, ACCENT_PRIMARY],
                [1,   ACCENT_SECONDARY],
            ],
        )
        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_layout(**PLOTLY_LAYOUT, height=500)
        fig_map.update_coloraxes(colorbar=dict(
            title=dict(text="Muertes", font=dict(color=TEXT_SECONDARY)),
            tickfont=dict(color=TEXT_SECONDARY),
        ))
        st.plotly_chart(fig_map, use_container_width=True)

    with col_rank:
        _sec("Top 10 Departamentos")
        dep_df = (
            fdf.groupby("DEPARTAMENTO").size()
            .reset_index(name="n")
            .sort_values("n", ascending=False)
            .head(10).sort_values("n")
        )
        n = len(dep_df)
        colors = [ACCENT_PRIMARY if i == n - 1 else ACCENT_TERTIARY for i in range(n)]

        fig_rank = go.Figure(go.Bar(
            x=dep_df["n"], y=dep_df["DEPARTAMENTO"], orientation="h",
            marker_color=colors,
            text=dep_df["n"].apply(lambda x: f"{x:,}"),
            textposition="outside",
        ))
        fig_rank.update_layout(
            **PLOTLY_LAYOUT, height=500,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        )
        st.plotly_chart(fig_rank, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA CAUSAS
# ─────────────────────────────────────────────────────────────────────────────

def page_causas(fdf: pd.DataFrame) -> None:
    """
    Vista Causas: análisis de la clasificación CIE-10.

    Secciones
    ---------
    1. Top 15 causas de muerte a nivel de código de 4 caracteres.
    2. Top 10 capítulos CIE-10 (categorías de enfermedad).
    """
    col_causas, col_capitulos = st.columns(2)

    _layout_causas = dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=TEXT_SECONDARY, family="Inter, sans-serif", size=11),
        height=550,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )

    with col_causas:
        _sec("Top 15 Causas de Muerte")
        causas_df = fdf["desc4"].value_counts().head(15).reset_index()
        causas_df.columns = ["Causa", "Cantidad"]
        causas_df = causas_df.sort_values("Cantidad")
        causas_df["Causa"] = causas_df["Causa"].apply(
            lambda x: x[:40] + "..." if len(str(x)) > 40 else x
        )

        fig_causas = go.Figure(go.Bar(
            x=causas_df["Cantidad"], y=causas_df["Causa"], orientation="h",
            marker_color=ACCENT_PRIMARY,
            text=causas_df["Cantidad"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Muertes: %{x:,}<extra></extra>",
        ))
        fig_causas.update_layout(
            **_layout_causas, margin=dict(l=140, r=80, t=12, b=8),
            yaxis=dict(tickfont=dict(size=9, color=TEXT_SECONDARY)),
        )
        st.plotly_chart(fig_causas, use_container_width=True)

    with col_capitulos:
        _sec("Capítulos CIE-10")
        cap_df = fdf["nom_cap"].dropna().value_counts().head(10).reset_index()
        cap_df.columns = ["Capitulo", "Cantidad"]
        cap_df = cap_df.sort_values("Cantidad")
        cap_df["Capitulo"] = cap_df["Capitulo"].apply(
            lambda x: x[:35] + "..." if len(str(x)) > 35 else x
        )

        fig_cap = go.Figure(go.Bar(
            x=cap_df["Cantidad"], y=cap_df["Capitulo"], orientation="h",
            marker_color=ACCENT_SECONDARY,
            text=cap_df["Cantidad"].apply(lambda x: f"{x:,}"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Muertes: %{x:,}<extra></extra>",
        ))
        fig_cap.update_layout(
            **_layout_causas, margin=dict(l=160, r=80, t=12, b=8),
            yaxis=dict(tickfont=dict(size=9, color=TEXT_SECONDARY)),
        )
        st.plotly_chart(fig_cap, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# PÁGINA DEMOGRAFÍA
# ─────────────────────────────────────────────────────────────────────────────

def page_demografia(fdf: pd.DataFrame) -> None:
    """
    Vista Demografía: perfil sociodemográfico de las defunciones.

    Secciones
    ---------
    1. Pirámide poblacional (masculino/femenino por grupo de edad).
    2. Distribución por estado civil (dona).
    3. Distribución por nivel educativo (barras).
    """
    col_pyramid, col_stats = st.columns(2)

    with col_pyramid:
        _sec("Pirámide Poblacional")
        pyramid = (
            fdf[fdf["SEXO_L"].isin(["Masculino", "Femenino"])]
            .groupby(["EDAD_L", "SEXO_L"]).size().reset_index(name="n")
        )
        pyramid["EDAD_L"] = pd.Categorical(pyramid["EDAD_L"], categories=EDAD_ORDER, ordered=True)
        pyramid = pyramid.dropna().sort_values("EDAD_L")

        male   = pyramid[pyramid["SEXO_L"] == "Masculino"].set_index("EDAD_L")["n"]
        female = pyramid[pyramid["SEXO_L"] == "Femenino"].set_index("EDAD_L")["n"]
        ages   = [a for a in EDAD_ORDER if a in male.index or a in female.index]

        fig_p = go.Figure()
        fig_p.add_trace(go.Bar(
            y=ages, x=[-male.get(a, 0) for a in ages],
            orientation="h", name="Masculino", marker_color=ACCENT_PRIMARY,
        ))
        fig_p.add_trace(go.Bar(
            y=ages, x=[female.get(a, 0) for a in ages],
            orientation="h", name="Femenino", marker_color=ACCENT_SECONDARY,
        ))
        fig_p.update_layout(
            **PLOTLY_LAYOUT, height=520, barmode="overlay",
            xaxis=dict(title="Cantidad", tickvals=[], zeroline=True, zerolinecolor=BORDER_COLOR),
        )
        st.plotly_chart(fig_p, use_container_width=True)

    with col_stats:
        _sec("Estado Civil")
        civil = fdf["ESTADO_CIVIL"].map(ESTADO_CIVIL_MAP).value_counts().reset_index()
        civil.columns = ["Estado", "Cantidad"]

        fig_civil = go.Figure(go.Pie(
            labels=civil["Estado"], values=civil["Cantidad"], hole=0.5,
            marker_colors=[ACCENT_PRIMARY, ACCENT_SECONDARY, ACCENT_TERTIARY,
                           "#2563eb", "#1d4ed8", "#1e3a8a"],
        ))
        fig_civil.update_layout(**PLOTLY_LAYOUT, height=240)
        st.plotly_chart(fig_civil, use_container_width=True)

        _sec("Nivel Educativo")
        edu = fdf["NIVEL_EDUCATIVO"].map(NIVEL_EDUCATIVO_MAP).value_counts().reset_index()
        edu.columns = ["Nivel", "Cantidad"]

        fig_edu = go.Figure(go.Bar(
            x=edu["Nivel"], y=edu["Cantidad"],
            marker=dict(
                color=edu["Cantidad"],
                colorscale=[[0, BG_PRIMARY], [0.5, ACCENT_PRIMARY], [1, ACCENT_SECONDARY]],
                showscale=False,
            ),
            text=edu["Cantidad"].apply(lambda x: f"{x:,}"),
            textposition="outside",
        ))
        fig_edu.update_layout(
            **PLOTLY_LAYOUT, height=220,
            xaxis=dict(tickangle=-20),
            yaxis=dict(showticklabels=False),
        )
        st.plotly_chart(fig_edu, use_container_width=True)
