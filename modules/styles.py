"""
styles.py
---------
Estilos CSS globales de la aplicación.
Se inyectan una sola vez al inicio mediante ``st.markdown(..., unsafe_allow_html=True)``.

Principios de diseño aplicados
--------------------------------
- **60-30-10**: Azul marino oscuro (fondo) / Azul intermedio (sidebar, cards)
  / Azul brillante (acentos, KPIs).
- **Consistencia**: mismos patrones visuales en todas las vistas.
- **Jerarquía visual**: tamaños y pesos tipográficos definidos.
- **Contraste / Accesibilidad**: relación mínima WCAG 4.5:1 para texto normal.
- **Feedback inmediato**: transiciones en hover y estados activos visibles.
- **Proximidad / Similitud** (Gestalt): elementos relacionados agrupados
  con el mismo estilo visual.
"""

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

/* ── Fondo base (60 %) ───────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a0e1a !important;
    font-family: 'Inter', sans-serif;
}

h1, h2, h3, .kpi-value, .sec-title {
    font-family: 'Inter', sans-serif;
    font-weight: 600;
}

/* ── Sidebar (30 %) ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: #0f1423 !important;
    border-right: 1px solid #1e2a4a;
    padding: 1rem 0.5rem;
}
[data-testid="stSidebar"] * { color: #94a3b8; font-family: 'Inter', sans-serif; }

[data-testid="stHeader"]     { background: transparent !important; }
[data-testid="stDecoration"] { display: none; }
section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }

/* ── Tipografía ──────────────────────────────────────────────────────── */
.main-header h1 { font-size: 1.75rem; font-weight: 700; letter-spacing: -0.02em; }
.main-header p  { font-size: 0.75rem; color: #64748b; margin-top: 0.25rem; }

.sec-title {
    font-size: 0.875rem; font-weight: 600; color: #3b82f6;
    letter-spacing: 0.05em; text-transform: uppercase;
    border-left: 3px solid #3b82f6; padding-left: 0.75rem;
    margin-bottom: 1rem;
}

/* ── Controles del sidebar ───────────────────────────────────────────── */
.stSelectbox label, .stSlider label, .stMultiSelect label {
    color: #64748b !important; font-size: 0.7rem !important;
    font-weight: 500 !important; letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}
.stSelectbox > div > div {
    background: #1a2335 !important; border: 1px solid #2a3650 !important;
    color: #e2e8f0 !important; border-radius: 8px !important;
}
.stSelectbox > div > div:hover {
    border-color: #3b82f6 !important; transition: border-color 0.2s ease;
}
.stSlider > div > div > div > div {
    background: #3b82f6 !important; transition: all 0.2s ease;
}
.stSlider > div > div > div > div:hover {
    transform: scale(1.1); background: #60a5fa !important;
}
button[kind="secondary"] { transition: all 0.2s ease !important; }
button[kind="secondary"]:hover {
    background: #1e2a4a !important; transform: translateY(-1px);
}

/* ── KPI Cards (10 % acento) ─────────────────────────────────────────── */
.kpi-card {
    background: linear-gradient(135deg, #0f1423 0%, #131a2c 100%);
    border: 1px solid #1e2a4a; border-radius: 12px;
    padding: 1.25rem; text-align: center;
    transition: all 0.25s ease; position: relative; overflow: hidden;
}
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, #3b82f6, #60a5fa);
    transform: scaleX(0); transition: transform 0.3s ease;
}
.kpi-card:hover::before { transform: scaleX(1); }
.kpi-card:hover {
    border-color: #3b82f6; transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(59,130,246,0.15);
}
.kpi-card.main-kpi {
    border-left: 3px solid #3b82f6;
    background: linear-gradient(135deg, #0f1423 0%, #1a2335 100%);
}
.kpi-label {
    color: #64748b; font-size: 0.7rem; font-weight: 600;
    letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.5rem;
}
.kpi-value {
    font-size: 2rem; font-weight: 700; color: #3b82f6;
    line-height: 1.2; letter-spacing: -0.02em;
}
.kpi-value.secondary { color: #60a5fa; font-size: 1.75rem; }
.kpi-sub { color: #475569; font-size: 0.7rem; margin-top: 0.5rem; }

/* ── Divisores / espaciado ───────────────────────────────────────────── */
hr { border-color: #1e2a4a; margin: 1rem 0; }
.block-container { padding: 1.5rem 2rem !important; }

/* ── Scrollbar personalizada ─────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f1423; border-radius: 3px; }
::-webkit-scrollbar-thumb { background: #3b82f6; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #60a5fa; }

/* ── Botones de navegación ───────────────────────────────────────────── */
.nav-button {
    background: transparent; border: 1px solid #1e2a4a; border-radius: 8px;
    padding: 0.6rem; font-size: 0.8rem; font-weight: 500;
    color: #94a3b8; transition: all 0.2s ease; cursor: pointer; text-align: center;
}
.nav-button:hover { border-color: #3b82f6; color: #e2e8f0; background: rgba(59,130,246,0.1); }
.nav-button.active { background: #3b82f6; border-color: #3b82f6; color: white; }

/* ── Expander ────────────────────────────────────────────────────────── */
.streamlit-expanderHeader {
    color: #64748b !important; font-size: 0.75rem !important; font-weight: 500 !important;
}
.streamlit-expanderContent {
    background: #0f1423 !important; border: 1px solid #1e2a4a; border-radius: 8px;
}
</style>
"""


def inject_styles():
    """Inyecta los estilos CSS globales en la aplicación Streamlit."""
    import streamlit as st
    st.markdown(APP_CSS, unsafe_allow_html=True)
