"""Linea base y modelos candidatos. Todos son Pipelines: el escalado se ajusta DENTRO de cada pliegue.

Orden de complejidad (de mas simple a mas complejo) usado por el criterio de seleccion (seleccion.py):
regresion logistica < arbol < Random Forest < boosting.
"""
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

SEMILLA = 42
LINEA_BASE = "linea_base"
COMPLEJIDAD = ["regresion_logistica", "arbol", "random_forest", "boosting"]


def crear_modelos():
    """Diccionario nombre -> estimador sin ajustar (la linea base va primero)."""
    return {
        LINEA_BASE: DummyClassifier(strategy="most_frequent"),
        "regresion_logistica": Pipeline([
            ("escalado", StandardScaler()),
            ("modelo", LogisticRegression(max_iter=1000, random_state=SEMILLA)),
        ]),
        "arbol": Pipeline([
            ("modelo", DecisionTreeClassifier(max_depth=3, random_state=SEMILLA)),
        ]),
        "random_forest": Pipeline([
            ("modelo", RandomForestClassifier(n_estimators=200, random_state=SEMILLA)),
        ]),
        "boosting": Pipeline([
            ("modelo", HistGradientBoostingClassifier(random_state=SEMILLA)),
        ]),
    }
