"""Cargador de datos de German Credit (Rol 1: Analista de datos).

Devuelve los datos SIN transformar: no codifica, no escala, no particiona.
La codificacion/escalado debe hacerla el ingeniero dentro de un Pipeline.
"""
from pathlib import Path

import pandas as pd

RUTA_POR_DEFECTO = Path(__file__).resolve().parent.parent / "datos" / "credit_g.csv"
COL_OBJETIVO = "clase"
CLASE_POSITIVA = "bad"  # 1 = credito malo, 0 = credito bueno


def cargar_datos(ruta=RUTA_POR_DEFECTO):
    """Lee el CSV y devuelve (X, y, cols_cat).

    X        : DataFrame de caracteristicas, tal como vienen en el archivo.
    y        : Serie de enteros, 1 = 'bad', 0 = 'good'.
    cols_cat : lista con los nombres de las columnas de texto (categoricas).

    Solo '' se interpreta como valor faltante; textos como 'none' o 'NA' se
    conservan como categorias validas (no se convierten a NaN).
    """
    ruta = Path(ruta)
    df = pd.read_csv(ruta, keep_default_na=False, na_values=[""])
    valores = set(df[COL_OBJETIVO].unique())
    if not valores <= {"good", CLASE_POSITIVA}:
        raise ValueError(f"Valores inesperados en '{COL_OBJETIVO}': {sorted(valores)}")
    y = (df[COL_OBJETIVO] == CLASE_POSITIVA).astype(int).rename(COL_OBJETIVO)
    X = df.drop(columns=[COL_OBJETIVO])
    cols_cat = X.select_dtypes(include=["object", "string"]).columns.tolist()
    return X, y, cols_cat


if __name__ == "__main__":
    X, y, cols_cat = cargar_datos()
    print("X:", X.shape, "| y=1 (bad):", int(y.sum()), "| categoricas:", len(cols_cat))
