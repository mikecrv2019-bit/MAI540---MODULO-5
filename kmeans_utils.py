"""
Lógica de K-Means del servidor: igual que pca_utils.py, nada de esto sabe que
existe MCP. mcp_server.py solo envuelve estas funciones con @mcp.tool.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from pca_utils import cargar_dataset


def cargar_y_escalar(nombre: str) -> tuple[np.ndarray, list[str]]:
    """Carga un dataset y estandariza sus columnas numéricas (media 0, desv. 1).

    Devuelve la matriz escalada y los nombres de las columnas usadas. Las
    columnas categóricas (p. ej. 'species', 'cultivar') se excluyen: K-Means no
    las ve, así que no hay fuga de la etiqueta real hacia los grupos.
    """
    df = cargar_dataset(nombre)
    numericas = df.select_dtypes(include="number").columns.tolist()
    if not numericas:
        raise ValueError(f"'{nombre}' no tiene columnas numéricas para aplicar K-Means.")
    X = df[numericas].dropna()
    return StandardScaler().fit_transform(X), numericas


def ejecutar_kmeans(nombre: str, k: int) -> dict:
    """
    Ejecuta K-Means con k grupos sobre las columnas numéricas escaladas.

    Devuelve las etiquetas de grupo de cada fila, el tamaño de cada grupo, la
    inercia (suma de distancias cuadradas al centroide) y el coeficiente de
    silueta promedio.
    """
    X, numericas = cargar_y_escalar(nombre)
    if k < 2 or k >= len(X):
        raise ValueError(
            f"k debe estar entre 2 y {len(X) - 1} (la silueta requiere al menos "
            f"2 grupos y menos grupos que filas; '{nombre}' tiene {len(X)} filas)."
        )

    modelo = KMeans(n_clusters=k, n_init=10, random_state=42)
    etiquetas = modelo.fit_predict(X)
    tamanos = pd.Series(etiquetas).value_counts().sort_index()

    return {
        "dataset": nombre,
        "filas_usadas": len(X),
        "variables_usadas": numericas,
        "k": k,
        "etiquetas": [int(e) for e in etiquetas],
        "tamano_por_grupo": {int(g): int(n) for g, n in tamanos.items()},
        "inercia": round(float(modelo.inertia_), 4),
        "silueta": round(float(silhouette_score(X, etiquetas)), 4),
    }
