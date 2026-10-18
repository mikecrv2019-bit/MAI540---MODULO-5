"""Comandos reutilizables del proyecto.  Uso:  python tareas.py evaluar | auditar | probar"""
import subprocess
import sys

import pandas as pd
from sklearn.model_selection import cross_val_score, StratifiedKFold   # validación cruzada (Clase 6)

from datos import cargar_datos
from predictor import entrenar_predictor


def evaluar():
    """Exactitud del predictor con validación cruzada de 5 pliegues."""
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OrdinalEncoder
    X, y, cols_cat, _ = cargar_datos()
    prep = ColumnTransformer([("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), cols_cat)], remainder="passthrough")
    pipe = Pipeline([("prep", prep), ("modelo", RandomForestClassifier(n_estimators=200, random_state=42))])
    scores = cross_val_score(pipe, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=42))
    print(f"Exactitud: {scores.mean():.3f} ± {scores.std():.3f}")


def auditar():
    """Exactitud por rango de edad, sobre los casos de prueba."""
    predictor, X_pru, y_pru = entrenar_predictor()
    acierto = predictor.predict(X_pru) == y_pru.values
    rango = pd.cut(X_pru["age"], [0, 25, 35, 50, 100], labels=["hasta 25", "26-35", "36-50", "más de 50"])
    print(X_pru.assign(acierto=acierto, edad=rango).groupby("edad", observed=True)["acierto"]
          .agg(exactitud="mean", casos="count").round(2))


def probar():
    """Ejecuta las pruebas automáticas."""
    sys.exit(subprocess.call([sys.executable, "-m", "pytest", "-q"]))


COMANDOS = {"evaluar": evaluar, "auditar": auditar, "probar": probar}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in COMANDOS:
        sys.exit("Uso: python tareas.py " + " | ".join(COMANDOS))
    COMANDOS[sys.argv[1]]()
