"""K-Means exploratorio de la propuesta (Modulo 5.2): silueta y estabilidad de los 3 grupos.

Criterios de exito de la propuesta que se verifican aqui:
  (a) silueta >= la del piloto, 0.2849;   (b) grupos estables al remuestrear.
K-Means no usa la etiqueta: solo las 13 variables estandarizadas. `cultivar` entra solo para medir el acuerdo (ARI).
"""
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

SEMILLA = 42
K = 3
SILUETA_PILOTO = 0.2849
N_REMUESTREOS = 30


def _kmeans(Xe, semilla):
    return KMeans(n_clusters=K, n_init=10, random_state=semilla).fit(Xe)


def segmentar(X, y=None, n_remuestreos=N_REMUESTREOS):
    """Silueta de K-Means (k=3), acuerdo con `cultivar` y estabilidad por remuestreo bootstrap.

    Estabilidad: en cada remuestreo se ajusta (escalado incluido) con filas tomadas con reemplazo, se asigna
    cada fila original al centroide mas cercano y se compara con los grupos de la muestra completa (ARI).
    """
    Xe = StandardScaler().fit_transform(X)
    base = _kmeans(Xe, SEMILLA)
    etiquetas = base.labels_
    rng = np.random.default_rng(SEMILLA)
    aris = []
    for _ in range(n_remuestreos):
        idx = rng.integers(0, len(X), len(X))
        esc = StandardScaler().fit(X.iloc[idx])
        modelo = _kmeans(esc.transform(X.iloc[idx]), int(rng.integers(0, 10_000)))
        aris.append(adjusted_rand_score(etiquetas, modelo.predict(esc.transform(X))))
    salida = {
        "k": K,
        "silueta": float(silhouette_score(Xe, etiquetas)),
        "silueta_piloto": SILUETA_PILOTO,
        "tamano_por_grupo": {int(g): int((etiquetas == g).sum()) for g in sorted(set(etiquetas))},
        "estabilidad_ari": {"media": float(np.mean(aris)), "desv": float(np.std(aris, ddof=1)),
                            "min": float(np.min(aris)), "n_remuestreos": n_remuestreos},
    }
    if y is not None:
        salida["ari_vs_cultivar"] = float(adjusted_rand_score(y, etiquetas))
    return salida
