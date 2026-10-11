"""Protocolo de evaluacion unico (Tarea 6.2): la MISMA funcion y la MISMA validacion cruzada para todos.

Validacion cruzada externa: StratifiedKFold(5, shuffle=True, random_state=42), igual que la Tarea 6.1.
`evaluar` ajusta una copia limpia del estimador en cada pliegue, mide el tiempo de ajuste y guarda las
predicciones fuera de pliegue (cada fila la predice un modelo que no la vio en el ajuste).
"""
import time

import numpy as np
from sklearn.base import clone
from sklearn.metrics import accuracy_score, confusion_matrix, recall_score
from sklearn.model_selection import StratifiedKFold

N_PLIEGUES = 5
SEMILLA_CV = 42
SEMILLA_CV_INTERNA = 43  # validacion cruzada interna de la busqueda anidada


def crear_cv(semilla=SEMILLA_CV):
    return StratifiedKFold(n_splits=N_PLIEGUES, shuffle=True, random_state=semilla)


def linea_base_siempre_bueno(y):
    """Exactitud de predecir siempre 'good' (y = 0)."""
    return float((np.asarray(y) == 0).mean())


def resumen(valores):
    """Media y desviacion estandar muestral (ddof=1) de los valores por pliegue."""
    a = np.asarray(valores, dtype=float)
    return {"media": float(a.mean()), "desv": float(a.std(ddof=1)),
            "min": float(a.min()), "max": float(a.max())}


def evaluar(estimador, X, y, cv):
    """Validacion cruzada con X, y y cv dados. Devuelve metricas por pliegue y predicciones fuera de pliegue.

    `estimador` puede ser un Pipeline o un GridSearchCV (validacion cruzada anidada: la busqueda se
    repite dentro de cada pliegue externo usando solo sus datos de entrenamiento).
    """
    pred = np.full(len(y), -1, dtype=int)
    exactitud, recall_bad, tiempos, ajustados = [], [], [], []
    for tr, te in cv.split(X, y):
        modelo = clone(estimador)
        t0 = time.perf_counter()
        modelo.fit(X.iloc[tr], y.iloc[tr])
        tiempos.append(time.perf_counter() - t0)
        p = modelo.predict(X.iloc[te])
        pred[te] = p
        exactitud.append(accuracy_score(y.iloc[te], p))
        recall_bad.append(recall_score(y.iloc[te], p, pos_label=1))
        ajustados.append(modelo)
    return {
        "exactitud_por_pliegue": [float(v) for v in exactitud],
        "recall_bad_por_pliegue": [float(v) for v in recall_bad],
        "tiempo_ajuste_por_pliegue_s": [float(v) for v in tiempos],
        "prediccion_fuera_de_pliegue": pred,
        "modelos_ajustados": ajustados,
    }


def matriz_y_metricas(y, pred):
    """Matriz de confusion (clase positiva = 1 = 'bad') y metricas derivadas, con la operacion explicita."""
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp),
        "exactitud": float((tp + tn) / (tp + tn + fp + fn)),          # (TP+TN)/total
        "recall_bad": float(tp / (tp + fn)),                           # TP/(TP+FN)
        "precision_bad": float(tp / (tp + fp)) if (tp + fp) else float("nan"),  # TP/(TP+FP)
    }
