"""Modelos y Pipeline (Tarea 6.2). Mismo preprocesamiento que la Tarea 6.1.

La codificacion ordinal de las categoricas va DENTRO del Pipeline, de modo que se ajusta solo con
los datos de entrenamiento de cada pliegue (y de cada pliegue interno de la busqueda).
Las numericas pasan sin transformar. Los tres modelos reciben exactamente el mismo X.
"""
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier

from datos import columnas_categoricas

SEMILLA_MODELO = 42


def crear_pipeline(estimador, X):
    """Pipeline = ColumnTransformer(OrdinalEncoder en categoricas, passthrough en numericas) + estimador.

    Las columnas se toman de X, que debe ser el X con el que se va a validar (ya sin sensibles).
    """
    cols_cat = columnas_categoricas(X)
    cols_num = [c for c in X.columns if c not in cols_cat]
    codificador = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    prep = ColumnTransformer(
        transformers=[("cat", codificador, cols_cat), ("num", "passthrough", cols_num)],
        remainder="drop",
    )
    # clone: cada Pipeline tiene su propio estimador; asi set_params en uno no contamina a otros
    return Pipeline([("prep", prep), ("modelo", clone(estimador))])


def estimadores_base():
    """Los tres modelos con parametros por defecto salvo la semilla.

    El arbol por defecto es el punto de partida de la busqueda (y la configuracion 'por defecto'
    de la comparacion); el arbol afinado sale de busqueda.py.
    """
    return {
        "arbol_defecto": DecisionTreeClassifier(random_state=SEMILLA_MODELO),
        "random_forest": RandomForestClassifier(random_state=SEMILLA_MODELO),
        "boosting_hgb": HistGradientBoostingClassifier(random_state=SEMILLA_MODELO),
    }


NOMBRES = {
    "arbol_defecto": "Árbol (por defecto)",
    "arbol_afinado": "Árbol afinado",
    "random_forest": "Random Forest",
    "boosting_hgb": "HistGradientBoosting",
}
