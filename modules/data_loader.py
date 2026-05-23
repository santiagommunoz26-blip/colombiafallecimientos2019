"""
data_loader.py
--------------
Funciones de carga y preprocesamiento de datos.
Aplica caché de Streamlit para evitar recargas en cada interacción.

Archivos requeridos (carpeta data/):
    - mortalidad_2019.xlsx  → registros de defunciones (DANE)
    - divipola.xlsx         → tabla de departamentos (código → nombre)
    - codigos_muerte.xlsx   → clasificación CIE-10
    - colombia.geojson      → geometrías departamentales
"""

import os
import json
import pandas as pd
import streamlit as st

from modules.text_utils import limpiar_texto, normalize_text
from modules.config import (
    SEXO_MAP, MESES_MAP, GRUPOS_EDAD_MAP,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Carga y une los tres Excel del proyecto.

    Pasos:
    1. Lee mortalidad_2019.xlsx y normaliza nombres de columna.
    2. Lee divipola.xlsx y aplica limpieza de texto a los nombres de departamento.
    3. Lee codigos_muerte.xlsx (CIE-10) y extrae la tabla desde la fila 8.
    4. Hace merge de los tres DataFrames.
    5. Agrega columnas legibles: SEXO_L, MES_L, EDAD_L.

    Returns
    -------
    pd.DataFrame
        DataFrame limpio y enriquecido con columnas adicionales.
    """
    base = os.path.dirname(os.path.dirname(__file__))

    # ── 1. Mortalidad ────────────────────────────────────────────────────────
    df = pd.read_excel(
        os.path.join(base, "data", "mortalidad_2019.xlsx"), engine="openpyxl"
    )
    df.columns = df.columns.str.strip()

    # Renombrar columna de año (puede llegar con tildes o caracteres raros)
    year_col = [c for c in df.columns if "A" in c.upper() and "O" in c.upper()]
    if year_col:
        df.rename(columns={year_col[0]: "ANO"}, inplace=True)

    # ── 2. DIVIPOLA ──────────────────────────────────────────────────────────
    div = pd.read_excel(
        os.path.join(base, "data", "divipola.xlsx"), engine="openpyxl"
    )
    div = div[["COD_DEPARTAMENTO", "DEPARTAMENTO"]].drop_duplicates()
    div["DEPARTAMENTO"] = div["DEPARTAMENTO"].apply(limpiar_texto)

    # ── 3. CIE-10 ────────────────────────────────────────────────────────────
    raw = pd.read_excel(
        os.path.join(base, "data", "codigos_muerte.xlsx"),
        engine="openpyxl",
        header=None,
    )
    cie = raw.iloc[8:].copy()
    cie.columns = ["cap", "nom_cap", "cod3", "desc3", "cod4", "desc4"]
    cie = cie.dropna(subset=["cod4"])
    cie["cod4"] = cie["cod4"].astype(str).str.strip()
    cie["nom_cap"] = cie["nom_cap"].apply(limpiar_texto)
    cie["desc4"] = cie["desc4"].apply(limpiar_texto)

    # ── 4. Merges ────────────────────────────────────────────────────────────
    df = df.merge(div, on="COD_DEPARTAMENTO", how="left")
    if "DEPARTAMENTO" in df.columns:
        df["DEPARTAMENTO"] = df["DEPARTAMENTO"].apply(limpiar_texto)

    df["COD_MUERTE"] = df["COD_MUERTE"].astype(str).str.strip()
    df = df.merge(
        cie[["cod4", "desc4", "nom_cap"]],
        left_on="COD_MUERTE",
        right_on="cod4",
        how="left",
    )

    # ── 5. Columnas legibles ─────────────────────────────────────────────────
    df["SEXO_L"] = df["SEXO"].map(SEXO_MAP)
    df["MES_L"]  = df["MES"].map(MESES_MAP)
    df["EDAD_L"] = df["GRUPO_EDAD1"].map(GRUPOS_EDAD_MAP).fillna("Sin dato")

    return df


@st.cache_data
def load_geo() -> dict:
    """
    Carga el GeoJSON de Colombia y normaliza los nombres de propiedades.

    Agrega una clave ``<prop>_norm`` (ASCII, mayúsculas) para cada propiedad
    de tipo texto, facilitando los joins con el DataFrame de mortalidad.

    Returns
    -------
    dict
        GeoJSON con propiedades enriquecidas.
    """
    base = os.path.dirname(os.path.dirname(__file__))
    path = os.path.join(base, "colombia.geojson")

    with open(path, "r", encoding="utf-8") as f:
        geo = json.load(f)

    for feature in geo["features"]:
        props = feature["properties"]
        new_props = {}
        for key, value in props.items():
            if isinstance(value, str) and any(
                kw in key.upper() for kw in ("DPTO", "DEP", "NOMBRE")
            ):
                value = limpiar_texto(value)
            new_props[key] = value
            new_props[key + "_norm"] = (
                normalize_text(value) if isinstance(value, str) else value
            )
        feature["properties"] = new_props

    return geo


def detect_geo_id(geo: dict) -> str:
    """
    Detecta automáticamente la clave de ID en el GeoJSON.

    Parameters
    ----------
    geo : dict
        GeoJSON cargado por :func:`load_geo`.

    Returns
    -------
    str
        Nombre de la propiedad a usar como identificador geográfico.
    """
    if geo is None:
        return "DPTO"
    feat0 = geo["features"][0]["properties"]
    possible_keys = ["DPTO", "dpto", "COD_DPTO", "codigo", "CODIGO", "id",
                     "DPTO_norm", "dpto_norm"]
    return next((k for k in possible_keys if k in feat0), list(feat0.keys())[0])
