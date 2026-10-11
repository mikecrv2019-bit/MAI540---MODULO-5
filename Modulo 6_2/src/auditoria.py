"""Auditoria por subgrupo del modelo elegido (insumo de la Skill auditoria-modelos, criterios V4).

Las variables sensibles NO son predictoras: aqui solo sirven para agrupar las predicciones fuera de
pliegue (cada fila la predijo un modelo que no la vio) y medir si el modelo falla mas con algun grupo.

Metrica prioritaria: recall de la clase 'bad' (aprobar un credito malo es el error caro; ver README).
Umbral de disparidad: 0.10 de diferencia absoluta frente al recall global.
Tamano minimo: 20 casos positivos ('bad') en el subgrupo; con menos, un solo caso mueve el recall >= 0.05.
"""
import pandas as pd

UMBRAL_DISPARIDAD = 0.10
MIN_POSITIVOS = 20


def recall_por_subgrupo(y, pred, grupos, columna):
    """Tabla por valor de `columna`: n, positivos (bad), exactitud, recall de bad y diferencia con el recall global."""
    df = pd.DataFrame({"y": y.to_numpy(), "pred": pred, "grupo": grupos[columna].to_numpy()})
    recall_global = ((df.y == 1) & (df.pred == 1)).sum() / (df.y == 1).sum()
    filas = []
    for valor, g in df.groupby("grupo", sort=True):
        positivos = int((g.y == 1).sum())
        aciertos_pos = int(((g.y == 1) & (g.pred == 1)).sum())
        recall = aciertos_pos / positivos if positivos else float("nan")
        filas.append({
            "subgrupo": columna, "valor": str(valor), "n": int(len(g)), "positivos_bad": positivos,
            "aciertos_bad": aciertos_pos,                                   # TP del subgrupo
            "exactitud": float((g.y == g.pred).mean()),
            "recall_bad": float(recall),                                    # aciertos_bad / positivos_bad
            "dif_vs_global": float(recall - recall_global),                 # recall_subgrupo - recall_global
            "evaluable": positivos >= MIN_POSITIVOS,
            "supera_umbral": bool(positivos >= MIN_POSITIVOS and abs(recall - recall_global) > UMBRAL_DISPARIDAD),
        })
    return pd.DataFrame(filas), float(recall_global)
