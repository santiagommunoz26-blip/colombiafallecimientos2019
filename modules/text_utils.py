"""
text_utils.py
-------------
Funciones de limpieza y normalización de texto.
Se utilizan principalmente durante la carga de datos para corregir
problemas de encoding (latin-1 / UTF-8) y estandarizar nombres.
"""

import unicodedata
import pandas as pd


def limpiar_texto(texto) -> str:
    """
    Limpia y estandariza un campo de texto.

    Operaciones aplicadas:
    1. Maneja valores nulos (NaN / None) → devuelve cadena vacía.
    2. Intenta recodificar de latin-1 a UTF-8.
    3. Reemplaza secuencias de escape típicas de mala codificación.
    4. Elimina caracteres no imprimibles (excepto espacio y guión).
    5. Aplica `str.title()` para capitalización consistente.

    Parameters
    ----------
    texto : any
        Valor a limpiar (puede ser str, float, None, etc.).

    Returns
    -------
    str
        Texto limpio y capitalizado.
    """
    if pd.isna(texto) or texto is None:
        return ""

    texto = str(texto)

    # Intento de recodificación
    try:
        texto = texto.encode("latin1").decode("utf-8")
    except Exception:
        pass

    # Tabla de reemplazos por escape incorrecto
    replacements = {
        "Ã¡": "á",
        "Ã©": "é",
        "Ã­": "í",
        "Ã³": "ó",
        "Ãº": "ú",
        "Ã±": "ñ",
        "Ã'": "Ñ",
        "Ã\x81": "Á",
        "Ã‰": "É",
        "Ã“": "Ó",
        "Ãš": "Ú",
        "Ã¼": "ü",
        "ÃÄ": "Ä",
        "D.C.": "",
        ", D.C.": "",
        "Ã\x83": "Á",
    }
    for old, new in replacements.items():
        texto = texto.replace(old, new)

    # Eliminar caracteres no imprimibles
    texto = "".join(
        c for c in texto if c.isprintable() or c in (" ", "-")
    )

    return texto.strip().title()


def normalize_text(text) -> str:
    """
    Normaliza texto a ASCII puro en mayúsculas, sin tildes ni diacríticos.

    Se usa para construir claves de comparación y joins entre el GeoJSON
    y el DataFrame de mortalidad.

    Parameters
    ----------
    text : any
        Valor a normalizar.

    Returns
    -------
    str
        Texto en mayúsculas sin caracteres especiales.
    """
    if pd.isna(text) or text is None:
        return ""

    text = str(text)
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
    return text.strip().upper()
