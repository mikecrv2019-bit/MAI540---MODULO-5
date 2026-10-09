"""Rol 2: validacion cruzada estratificada (5 pliegues, shuffle, semilla 42)."""
import numpy as np
from sklearn.base import clone
from sklearn.metrics import recall_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_validate

N_PLIEGUES = 5
SEMILLA_CV = 42


def crear_cv():
    return StratifiedKFold(n_splits=N_PLIEGUES, shuffle=True, random_state=SEMILLA_CV)


def validar_cv(pipeline, X, y):
    """Exactitud y recall de 'bad' (y=1) por pliegue, mas el recall agregado
    de cross_val_predict (dato adicional, no sustituto)."""
    cv = crear_cv()
    res = cross_validate(
        clone(pipeline), X, y, cv=cv,
        scoring={"exactitud": "accuracy", "recall_bad": "recall"},
        n_jobs=1,
    )
    pred = cross_val_predict(clone(pipeline), X, y, cv=cv, n_jobs=1)
    return {
        "exactitud_por_pliegue": [float(v) for v in res["test_exactitud"]],
        "recall_bad_por_pliegue": [float(v) for v in res["test_recall_bad"]],
        "recall_bad_agregado_cross_val_predict": float(recall_score(y, pred, pos_label=1)),
    }


def resumen(valores, ddof=1):
    a = np.asarray(valores, dtype=float)
    return {
        "media": float(a.mean()),
        "desv": float(a.std(ddof=ddof)),
        "min": float(a.min()),
        "max": float(a.max()),
    }
