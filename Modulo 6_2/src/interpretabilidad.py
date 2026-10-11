"""Importancia por permutacion del modelo elegido, medida en los pliegues de PRUEBA.

Para cada pliegue se ajusta el modelo con el entrenamiento y se mide cuanto cae la exactitud del pliegue de
prueba al barajar una variable (n_repeats veces). Es una explicacion global y aproximada: dice que variables
usa el modelo, no la regla exacta de cada decision.
"""
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.inspection import permutation_importance

N_REPETICIONES = 10
SEMILLA = 42


def importancia_por_permutacion(estimador, X, y, cv):
    """DataFrame (variable, caida media de exactitud, desviacion entre pliegues), ordenado de mayor a menor."""
    caidas = []
    for tr, te in cv.split(X, y):
        modelo = clone(estimador).fit(X.iloc[tr], y.iloc[tr])
        r = permutation_importance(modelo, X.iloc[te], y.iloc[te], scoring="accuracy",
                                   n_repeats=N_REPETICIONES, random_state=SEMILLA, n_jobs=1)
        caidas.append(r.importances_mean)
    caidas = np.asarray(caidas)
    return (pd.DataFrame({"variable": list(X.columns), "caida_exactitud_media": caidas.mean(axis=0),
                          "desv_entre_pliegues": caidas.std(axis=0, ddof=1)})
            .sort_values("caida_exactitud_media", ascending=False).reset_index(drop=True))
