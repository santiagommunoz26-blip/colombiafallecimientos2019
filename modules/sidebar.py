"""
sidebar.py
----------
Renderizado del sidebar: cabecera de marca, navegación entre páginas
y todos los filtros interactivos.

La función principal ``render_sidebar`` devuelve un diccionario con
los valores seleccionados por el usuario y aplica los filtros al DataFrame.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from modules.config import (
    ACCENT_PRIMARY, TEXT_MUTED, PAGES,
    EDAD_ORDER,
)


def render_sidebar(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Dibuja el sidebar y aplica los filtros al DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame completo cargado por ``load_data()``.

    Returns
    -------
    fdf : pd.DataFrame
        DataFrame filtrado según las selecciones del usuario.
    filters : dict
        Valores actuales de cada filtro (útiles para el header y el nombre
        del archivo CSV de descarga).
    """
    with st.sidebar:
        # ── Cabecera ──────────────────────────────────────────────────────
        st.markdown(f"""
        <div style='text-align:center;padding:0.5rem 0 1.5rem 0'>
            <div style='font-size:1.75rem;font-weight:700;color:{ACCENT_PRIMARY};
                        letter-spacing:2px'>MORTALIDAD</div>
            <div style='font-size:0.7rem;color:{TEXT_MUTED};letter-spacing:2px'>
                COLOMBIA · 2019</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Navegación ────────────────────────────────────────────────────
        if "page" not in st.session_state:
            st.session_state.page = "General"

        st.markdown(
            f'<div style="font-size:0.65rem;color:{TEXT_MUTED};'
            f'letter-spacing:2px;margin-bottom:0.75rem">NAVEGACION</div>',
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns(2)
        for i, page_name in enumerate(PAGES):
            col = col1 if i < 2 else col2
            with col:
                if st.button(page_name, key=f"nav_{page_name}", use_container_width=True):
                    st.session_state.page = page_name

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── Filtros principales ───────────────────────────────────────────
        st.markdown(
            f'<div style="font-size:0.65rem;color:{TEXT_MUTED};'
            f'letter-spacing:2px;margin-bottom:0.75rem">FILTROS</div>',
            unsafe_allow_html=True,
        )

        maneras = ["Todas"] + sorted(df["MANERA_MUERTE"].dropna().unique().tolist())
        sel_manera = st.selectbox("Manera de muerte", maneras)

        sel_sexo = st.selectbox("Sexo", ["Todos", "Masculino", "Femenino"])

        deptos = sorted(df["DEPARTAMENTO"].dropna().unique().tolist())
        sel_depto = st.selectbox("Departamento", ["Todos"] + deptos)

        mes_r = st.slider("Rango de meses", 1, 12, (1, 12), format="%d")

        # ── Filtros secundarios ───────────────────────────────────────────
        st.markdown("---")
        st.markdown(
            f'<div style="font-size:0.65rem;color:{TEXT_MUTED};'
            f'letter-spacing:2px;margin-bottom:0.75rem">FILTRO POR EDAD</div>',
            unsafe_allow_html=True,
        )
        sel_edad = st.selectbox("Grupo de edad", ["Todas"] + EDAD_ORDER)

        st.markdown("---")
        st.markdown(
            f'<div style="font-size:0.65rem;color:{TEXT_MUTED};'
            f'letter-spacing:2px;margin-bottom:0.75rem">FILTRO POR CAUSA</div>',
            unsafe_allow_html=True,
        )
        causas_opts = ["Todas"] + sorted(df["desc4"].dropna().unique().tolist())
        sel_causa = st.selectbox("Causa de muerte (CIE-10)", causas_opts)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.7rem;color:{TEXT_MUTED};text-align:center">'
            f'{len(df):,} registros totales<br>Fuente: DANE 2019</div>',
            unsafe_allow_html=True,
        )

    # ── Aplicar filtros ───────────────────────────────────────────────────
    fdf = df.copy()
    if sel_manera != "Todas":
        fdf = fdf[fdf["MANERA_MUERTE"] == sel_manera]
    if sel_sexo != "Todos":
        fdf = fdf[fdf["SEXO_L"] == sel_sexo]
    if sel_depto != "Todos":
        fdf = fdf[fdf["DEPARTAMENTO"] == sel_depto]
    fdf = fdf[(fdf["MES"] >= mes_r[0]) & (fdf["MES"] <= mes_r[1])]
    if sel_edad != "Todas":
        fdf = fdf[fdf["EDAD_L"] == sel_edad]
    if sel_causa != "Todas":
        fdf = fdf[fdf["desc4"] == sel_causa]

    filters = dict(
        manera=sel_manera,
        sexo=sel_sexo,
        depto=sel_depto,
        mes_r=mes_r,
        edad=sel_edad,
        causa=sel_causa,
    )

    return fdf, filters


def render_download_button(fdf: pd.DataFrame, filters: dict) -> None:
    """
    Agrega el botón de descarga CSV al final del sidebar.

    Parameters
    ----------
    fdf : pd.DataFrame
        DataFrame ya filtrado.
    filters : dict
        Diccionario de filtros activos (para nombrar el archivo).
    """
    causa_slug = (
        filters["causa"][:20] if filters["causa"] != "Todas" else "Todas"
    )
    nombre = (
        f"mortalidad_manera_{filters['manera']}_sexo_{filters['sexo']}"
        f"_depto_{filters['depto']}_meses_{filters['mes_r'][0]}"
        f"_{filters['mes_r'][1]}_edad_{filters['edad']}_causa_{causa_slug}.csv"
    )

    with st.sidebar:
        st.markdown("<hr>", unsafe_allow_html=True)
        if len(fdf) > 0:
            csv_data = fdf.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "Descargar CSV",
                csv_data,
                nombre,
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.button("Descargar CSV", disabled=True, use_container_width=True)
