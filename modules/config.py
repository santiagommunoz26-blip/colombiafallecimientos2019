"""
config.py
---------
Constantes globales de la aplicación: paleta de colores, layout de Plotly
y mapeos de variables categóricas.
"""

# ============================================================
# PALETA DE COLORES — Regla 60-30-10
# 60 % → Azul marino oscuro (fondo base)
# 30 % → Azul intermedio (sidebar, tarjetas)
# 10 % → Azul brillante (acentos, KPIs, interactivos)
# ============================================================
BG_PRIMARY       = "#0a0e1a"
BG_SECONDARY     = "#0f1423"
BG_CARD          = "#131a2c"
ACCENT_PRIMARY   = "#3b82f6"
ACCENT_SECONDARY = "#60a5fa"
ACCENT_TERTIARY  = "#93c5fd"
TEXT_PRIMARY     = "#f8fafc"
TEXT_SECONDARY   = "#94a3b8"
TEXT_MUTED       = "#64748b"
BORDER_COLOR     = "#1e2a4a"

# ============================================================
# LAYOUT BASE PARA PLOTLY
# ============================================================
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT_SECONDARY, family="Inter, sans-serif", size=11),
    margin=dict(l=8, r=8, t=12, b=8),
    hovermode="x unified",
)

# ============================================================
# MAPEOS DE VARIABLES CATEGÓRICAS
# ============================================================
SEXO_MAP = {1: "Masculino", 2: "Femenino", 3: "Indeterminado"}

MESES_MAP = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}

MESES_ORD = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
             "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

GRUPOS_EDAD_MAP = {
    0: "<1 año", 1: "1-4",   2: "5-9",   3: "10-14",  4: "15-19",
    5: "20-24",  6: "25-29", 7: "30-34", 8: "35-39",  9: "40-44",
   10: "45-49", 11: "50-54",12: "55-59",13: "60-64", 14: "65-69",
   15: "70-74", 16: "75-79",17: "80-84",18: "85-89", 19: "90-94",
   20: "95-99", 21: "100+",
}

EDAD_ORDER = [
    "<1 año", "1-4", "5-9", "10-14", "15-19", "20-24", "25-29",
    "30-34", "35-39", "40-44", "45-49", "50-54", "55-59", "60-64",
    "65-69", "70-74", "75-79", "80-84", "85-89", "90-94", "95-99", "100+",
]

ESTADO_CIVIL_MAP = {
    1: "Soltero", 2: "Casado", 3: "Viudo",
    4: "Separado", 5: "Unión libre", 6: "Sin dato",
}

NIVEL_EDUCATIVO_MAP = {
    1: "Preescolar", 2: "Primaria", 3: "Secundaria",
    4: "Media", 5: "Superior", 6: "Ninguno", 9: "Sin dato",
}

# Páginas de navegación
PAGES = ["General", "Territorio", "Causas", "Demografia"]
