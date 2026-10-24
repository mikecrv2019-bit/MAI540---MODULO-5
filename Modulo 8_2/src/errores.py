"""Analisis de errores por categoria: en que clases falla mas el modelo y con cual se confunde."""
import numpy as np
from sklearn.metrics import confusion_matrix

from datos import CLASES


def analisis_por_categoria(y_real, y_pred, clases=CLASES):
    """Recall, precision y F1 de cada clase, la matriz de confusion y los pares de clases mas confundidos."""
    cm = confusion_matrix(y_real, y_pred, labels=clases)
    por_clase = {}
    for i, clase in enumerate(clases):
        verdaderos = int(cm[i, i])
        reales, predichos = int(cm[i].sum()), int(cm[:, i].sum())
        recall = verdaderos / reales if reales else float("nan")            # TP / (TP + FN)
        precision = verdaderos / predichos if predichos else float("nan")   # TP / (TP + FP)
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        por_clase[clase] = {"n": reales, "recall": recall, "precision": precision, "f1": f1}
    confusiones = [
        {"real": clases[i], "predicho": clases[j], "n": int(cm[i, j])}
        for i in range(len(clases)) for j in range(len(clases)) if i != j and cm[i, j] > 0
    ]
    confusiones.sort(key=lambda c: -c["n"])
    return {
        "matriz_confusion": cm.tolist(),
        "clases": list(clases),
        "por_clase": por_clase,
        "confusiones": confusiones,
        "errores": int(cm.sum() - np.trace(cm)),
        "total": int(cm.sum()),
    }
