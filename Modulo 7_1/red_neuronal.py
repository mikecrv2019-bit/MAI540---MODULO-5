"""Paso 2 · Una red neuronal sencilla sobre los mismos datos, para ver capas y pesos."""
from sklearn.compose import ColumnTransformer
from sklearn.neural_network import MLPClassifier       # MLP: red neuronal de capas completamente conectadas
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # texto → columnas 0/1; números → misma escala


def crear_red(cols_cat, cols_num):
    """Pipeline con la preparación y una red de dos capas ocultas (16 y 8 neuronas)."""
    # TODO 3 (en clase): preparación (OneHot + escala) y MLPClassifier
    raise NotImplementedError("TODO 3: completar en clase")


def describir_red(red_entrenada):
    """Devuelve las neuronas de cada capa y el total de pesos que la red aprendió."""
    # TODO 4 (en clase): leer coefs_ e intercepts_ de la red entrenada
    raise NotImplementedError("TODO 4: completar en clase")
