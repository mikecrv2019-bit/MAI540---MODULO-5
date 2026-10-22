"""Protocolo de validacion unico: la MISMA particion y la MISMA validacion cruzada para todos los modelos.

1. Se aparta una prueba final (20 %, estratificada, semilla 42) que NO interviene en ninguna decision.
2. Sobre el 80 % restante se hace validacion cruzada estratificada 5 pliegues x 3 repeticiones (semilla 42).
3. Se reporta media y desviacion estandar muestral (ddof=1) de las 15 estimaciones por modelo.
"""
import numpy as np
from sklearn.base import clone
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold, train_test_split

SEMILLA = 42
FRACCION_PRUEBA = 0.20
N_PLIEGUES = 5
N_REPETICIONES = 3


def dividir(X, y):
    """Particion estratificada entrenamiento / prueba final."""
    return train_test_split(X, y, test_size=FRACCION_PRUEBA, stratify=y, random_state=SEMILLA)


def crear_cv():
    return RepeatedStratifiedKFold(n_splits=N_PLIEGUES, n_repeats=N_REPETICIONES, random_state=SEMILLA)


def resumen(valores):
    """Media y desviacion estandar muestral (ddof=1)."""
    a = np.asarray(valores, dtype=float)
    return {"media": float(a.mean()), "desv": float(a.std(ddof=1)), "min": float(a.min()), "max": float(a.max())}


def evaluar_cv(estimador, X, y, cv=None):
    """Validacion cruzada de un estimador. Cada pliegue ajusta una copia limpia (escalado incluido).

    Devuelve exactitud y F1 macro por pliegue, y las predicciones fuera de pliegue de la primera repeticion
    (cada fila la predice un modelo que no la vio), que sirven para el analisis de errores.
    """
    cv = cv or crear_cv()
    exactitud, f1_macro = [], []
    pred_oof = np.full(len(y), None, dtype=object)
    for i, (tr, te) in enumerate(cv.split(X, y)):
        modelo = clone(estimador).fit(X.iloc[tr], y.iloc[tr])
        p = modelo.predict(X.iloc[te])
        exactitud.append(accuracy_score(y.iloc[te], p))
        f1_macro.append(f1_score(y.iloc[te], p, average="macro"))
        if i < N_PLIEGUES:  # primera repeticion: los 5 pliegues cubren cada fila una vez
            pred_oof[te] = p
    if any(p is None for p in pred_oof):
        raise ValueError(f"El cv entregado no cubre todas las filas en sus primeros {N_PLIEGUES} pliegues; "
                         "use crear_cv() (5 pliegues por repeticion).")
    return {
        "exactitud": resumen(exactitud),
        "f1_macro": resumen(f1_macro),
        "exactitud_por_pliegue": [float(v) for v in exactitud],
        "f1_macro_por_pliegue": [float(v) for v in f1_macro],
        "prediccion_fuera_de_pliegue": pred_oof,
    }


def evaluar_prueba(estimador, X_tr, y_tr, X_te, y_te):
    """Ajusta con el entrenamiento y mide UNA vez sobre la prueba final."""
    modelo = clone(estimador).fit(X_tr, y_tr)
    p = modelo.predict(X_te)
    return {
        "exactitud": float(accuracy_score(y_te, p)),
        "f1_macro": float(f1_score(y_te, p, average="macro")),
        "prediccion": p,
        "modelo": modelo,
    }
