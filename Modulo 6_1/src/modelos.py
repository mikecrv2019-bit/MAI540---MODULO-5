"""Rol 2 (Ingeniero de modelos): definicion de los dos modelos y su Pipeline.

El unico preprocesamiento es la codificacion ordinal de las categoricas, dentro
del Pipeline (se ajusta solo con los datos de entrenamiento de cada particion).
Las numericas pasan sin transformar ('passthrough'). Sin escalado ni logaritmos.
"""
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from sklearn.tree import DecisionTreeClassifier

SEMILLA_MODELO = 42


def dos_modelos():
    """Devuelve {nombre: estimador} con parametros por defecto salvo la semilla."""
    return {
        "arbol": DecisionTreeClassifier(random_state=SEMILLA_MODELO),
        "random_forest": RandomForestClassifier(random_state=SEMILLA_MODELO),
    }


def crear_pipeline(estimador, cols_cat, cols_num):
    """Pipeline = ColumnTransformer(OrdinalEncoder en cat, passthrough en num) + estimador."""
    codificador = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)
    preprocesador = ColumnTransformer(
        transformers=[
            ("cat", codificador, list(cols_cat)),
            ("num", "passthrough", list(cols_num)),
        ],
        remainder="drop",
    )
    return Pipeline([("prep", preprocesador), ("modelo", estimador)])
