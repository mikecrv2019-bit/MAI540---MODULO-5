"""K-Means exploratorio de la propuesta (Modulo 5.2): silueta y estabilidad de los 3 grupos.

Criterios de exito de la propuesta que se verifican aqui:
  (a) silueta >= la del piloto, 0.2849;   (b) grupos estables al remuestrear.
K-Means no usa la etiqueta: solo las 13 variables estandarizadas. `cultivar` entra solo para medir el acuerdo (ARI).
Se ajusta con la particion de entrenamiento (la misma que el clasificador); la prueba final solo se asigna con `predict`.
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


def segmentar(X_tr, y_tr=None, X_te=None, y_te=None, n_remuestreos=N_REMUESTREOS):
    """K-Means (k=3) ajustado SOLO con el entrenamiento: silueta, acuerdo con `cultivar` y estabilidad.

    El escalador y K-Means se ajustan con `X_tr`. La prueba (si se entrega) solo se asigna al centroide mas cercano
    con `predict`, para medir el acuerdo con `cultivar` en filas que el K-Means no vio.
    Estabilidad: en cada remuestreo bootstrap del entrenamiento se ajusta (escalado incluido), se asigna cada fila
    del entrenamiento al centroide mas cercano y se compara con los grupos de la muestra completa (ARI).
    """
    esc = StandardScaler().fit(X_tr)
    Xe = esc.transform(X_tr)
    base = _kmeans(Xe, SEMILLA)
    etiquetas = base.labels_
    rng = np.random.default_rng(SEMILLA)
    aris = []
    for _ in range(n_remuestreos):
        idx = rng.integers(0, len(X_tr), len(X_tr))
        esc_b = StandardScaler().fit(X_tr.iloc[idx])
        modelo = _kmeans(esc_b.transform(X_tr.iloc[idx]), int(rng.integers(0, 10_000)))
        aris.append(adjusted_rand_score(etiquetas, modelo.predict(esc_b.transform(X_tr))))
    salida = {
        "k": K,
        "ajustado_con": len(X_tr),
        "silueta": float(silhouette_score(Xe, etiquetas)),
        "silueta_piloto": SILUETA_PILOTO,
        "tamano_por_grupo": {int(g): int((etiquetas == g).sum()) for g in sorted(set(etiquetas))},
        "estabilidad_ari": {"media": float(np.mean(aris)), "desv": float(np.std(aris, ddof=1)),
                            "min": float(np.min(aris)), "n_remuestreos": n_remuestreos},
    }
    if y_tr is not None:
        salida["ari_vs_cultivar_entrenamiento"] = float(adjusted_rand_score(y_tr, etiquetas))
    if X_te is not None and y_te is not None:
        salida["ari_vs_cultivar_prueba"] = float(adjusted_rand_score(y_te, base.predict(esc.transform(X_te))))
    return salida
