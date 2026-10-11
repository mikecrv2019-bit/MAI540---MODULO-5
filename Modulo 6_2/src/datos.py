"""Carga de German Credit (Tarea 6.2). Continua el cargador de la Tarea 6.1 (mismo CSV, mismo objetivo).

Devuelve los datos SIN transformar: la codificacion de las categoricas se hace dentro del Pipeline.
Las variables sensibles (edad, estado civil) se usan para AUDITAR, no para decidir: `predictoras`
las quita de X y `grupos_auditoria` las deja disponibles para el analisis por subgrupo.
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RUTA_POR_DEFECTO = RAIZ / "datos" / "credit_g.csv"
COL_OBJETIVO = "clase"
CLASE_POSITIVA = "bad"  # y = 1 -> credito malo; y = 0 -> credito bueno

# Variables sensibles: solo para auditar. No entran como predictoras del modelo.
VARIABLES_SENSIBLES = ["age", "personal_status"]
# Subgrupos que se auditan: edad (en grupos), estado civil y vivienda.
SUBGRUPOS_AUDITORIA = ["age_grupo", "personal_status", "housing"]
CORTES_EDAD = [0, 24, 34, 44, 200]
ETIQUETAS_EDAD = ["<25", "25-34", "35-44", ">=45"]


def cargar_datos(ruta=RUTA_POR_DEFECTO):
    """Lee el CSV y devuelve (X, y) con las 20 variables originales.

    y es un entero: 1 = 'bad', 0 = 'good'. Solo '' se lee como faltante; textos como 'none'
    son categorias validas (igual que en la Tarea 6.1).
    """
    df = pd.read_csv(Path(ruta), keep_default_na=False, na_values=[""])
    valores = set(df[COL_OBJETIVO].unique())
    if not valores <= {"good", CLASE_POSITIVA}:
        raise ValueError(f"Valores inesperados en '{COL_OBJETIVO}': {sorted(valores)}")
    y = (df[COL_OBJETIVO] == CLASE_POSITIVA).astype(int).rename(COL_OBJETIVO)
    X = df.drop(columns=[COL_OBJETIVO])
    return X, y


def predictoras(X, excluir=VARIABLES_SENSIBLES):
    """X sin las variables sensibles: las unicas columnas con las que el modelo decide."""
    return X.drop(columns=list(excluir))


def columnas_categoricas(X):
    return X.select_dtypes(include=["object", "string"]).columns.tolist()


def grupos_auditoria(X):
    """DataFrame con las columnas de subgrupo para auditar (alineado con X por indice)."""
    g = pd.DataFrame(index=X.index)
    g["age_grupo"] = pd.cut(X["age"], bins=CORTES_EDAD, labels=ETIQUETAS_EDAD).astype(str)
    g["personal_status"] = X["personal_status"]
    g["housing"] = X["housing"]
    return g


if __name__ == "__main__":
    X, y = cargar_datos()
    print("X:", X.shape, "| y=1 (bad):", int(y.sum()), "| predictoras:", predictoras(X).shape[1])
