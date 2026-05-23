"""
app.py
------
Punto de entrada de la aplicación Streamlit.

Orquesta la carga de datos, los estilos, el sidebar, los filtros
y el renderizado de cada página. Toda la lógica pesada está delegada
en los módulos del paquete ``modules/``.

Ejecución
---------
    streamlit run app.py
"""

import warnings
warnings.filterwarnings("ignore")

import streamlit as st

# ── Configuración de página (debe ser la primera llamada a Streamlit) ─────────
st.set_page_config(
    page_title="Mortalidad Colombia 2019",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Módulos propios ───────────────────────────────────────────────────────────
from modules.styles      import inject_styles
from modules.data_loader import load_data, load_geo, detect_geo_id
from modules.sidebar     import render_sidebar, render_download_button
from modules.config      import (
    BG_CARD, BG_SECONDARY, BORDER_COLOR,
    TEXT_PRIMARY, TEXT_MUTED, ACCENT_PRIMARY,
)
from modules.pages import (
    page_general,
    page_territorio,
    page_causas,
    page_demografia,
)

# ── Estilos globales ──────────────────────────────────────────────────────────
inject_styles()

# ── Carga de datos ────────────────────────────────────────────────────────────
with st.spinner("Cargando datos..."):
    df  = load_data()
    geo = load_geo()

GEO_ID = detect_geo_id(geo)

# ── Sidebar: navegación + filtros ────────────────────────────────────────────
fdf, filters = render_sidebar(df)

N = len(fdf)

render_download_button(fdf, filters)

# ── Validación de filtros ─────────────────────────────────────────────────────
if N == 0:
    st.warning("No hay datos con los filtros seleccionados. Ajusta los filtros para ver resultados.")
    st.stop()

# ── Header principal ──────────────────────────────────────────────────────────
page = st.session_state.get("page", "General")

st.markdown(f"""
<div style='background:linear-gradient(135deg,{BG_CARD} 0%,{BG_SECONDARY} 100%);
            border:1px solid {BORDER_COLOR};border-radius:12px;
            padding:1.25rem 1.5rem;margin-bottom:1.5rem'>
    <div style='display:flex;justify-content:space-between;align-items:center'>
        <div>
            <div style='font-size:1.5rem;font-weight:700;color:{TEXT_PRIMARY};
                        letter-spacing:-0.02em'>{page} — Mortalidad Colombia 2019</div>
            <div style='font-size:0.75rem;color:{TEXT_MUTED};margin-top:0.25rem'>
                Mostrando <span style='color:{ACCENT_PRIMARY};font-weight:600'>
                {N:,}</span> de {len(df):,} registros
            </div>
        </div>
        <div style='font-size:2.5rem;font-weight:700;color:{TEXT_MUTED};opacity:0.3'>2019</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Enrutamiento de páginas ───────────────────────────────────────────────────
if page == "General":
    page_general(fdf)
elif page == "Territorio":
    page_territorio(fdf, geo, GEO_ID)
elif page == "Causas":
    page_causas(fdf)
elif page == "Demografia":
    page_demografia(fdf)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='text-align:center;padding:1.5rem 0 0.5rem;
            border-top:1px solid {BORDER_COLOR};margin-top:1.5rem'>
    <span style='font-size:0.65rem;color:{TEXT_MUTED};letter-spacing:1px'>
        Fuente: DANE · Mortalidad No Fetal 2019 · {N:,} registros analizados
    </span>
</div>
""", unsafe_allow_html=True)
