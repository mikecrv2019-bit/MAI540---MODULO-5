"""Carga y validacion de los datos del capstone (UCI Wine, 178 lotes, 13 variables quimicas).

La variable objetivo es `cultivar` (class_0, class_1, class_2). En la propuesta del Modulo 5 se usaba solo para
contraste; aqui es la etiqueta que el modelo aprende a predecir a partir de la quimica del lote. Ninguna de las
13 predictoras se calcula a partir de la etiqueta (son mediciones de laboratorio).
"""
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RUTA_DATOS = RAIZ / "datos" / "wine.csv"

OBJETIVO = "cultivar"
CLASES = ["class_0", "class_1", "class_2"]
PREDICTORAS = [
    "alcohol", "malic_acid", "ash", "alcalinity_of_ash", "magnesium", "total_phenols", "flavanoids",
    "nonflavanoid_phenols", "proanthocyanins", "color_intensity", "hue", "od280/od315_of_diluted_wines",
    "proline",
]


def validar_datos(df):
    """Falla con un mensaje claro si los datos no cumplen lo que el modelo supone."""
    faltan = [c for c in PREDICTORAS + [OBJETIVO] if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas en los datos: {faltan}")
    num = df[PREDICTORAS]
    if not all(pd.api.types.is_numeric_dtype(num[c]) for c in PREDICTORAS):
        raise ValueError("Todas las predictoras deben ser numericas.")
    if num.isna().any().any() or not np.isfinite(num.to_numpy(dtype=float)).all():
        raise ValueError("Las predictoras contienen NaN o infinitos.")
    desconocidas = set(df[OBJETIVO].unique()) - set(CLASES)
    if desconocidas:
        raise ValueError(f"Clases desconocidas en '{OBJETIVO}': {sorted(desconocidas)}")
    return df


def cargar_datos(ruta=RUTA_DATOS):
    """Devuelve (X, y). X tiene solo las 13 predictoras; y es `cultivar`."""
    df = validar_datos(pd.read_csv(ruta))
    return df[PREDICTORAS].copy(), df[OBJETIVO].copy()
