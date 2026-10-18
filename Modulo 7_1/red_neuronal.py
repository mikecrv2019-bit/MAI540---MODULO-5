"""Paso 2 · Una red neuronal sencilla sobre los mismos datos, para ver capas y pesos."""
from sklearn.compose import ColumnTransformer
from sklearn.neural_network import MLPClassifier       # MLP: red neuronal de capas completamente conectadas
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler  # texto → columnas 0/1; números → misma escala


def crear_red(cols_cat, cols_num):
    """Pipeline con la preparación y una red de dos capas ocultas (16 y 8 neuronas)."""
    prep = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), cols_cat),   # cada categoría se vuelve una columna 0/1
        ("num", StandardScaler(), cols_num),                         # los números quedan en la misma escala
    ])
    red = MLPClassifier(hidden_layer_sizes=(16, 8), activation="relu", max_iter=1000, random_state=42)   # 2 capas ocultas
    return Pipeline([("prep", prep), ("red", red)])                  # preparar → red


def describir_red(red_entrenada):
    """Devuelve las neuronas de cada capa y el total de pesos que la red aprendió."""
    mlp = red_entrenada.named_steps["red"]                               # la red dentro del Pipeline
    capas = [mlp.coefs_[0].shape[0]] + [c.shape[1] for c in mlp.coefs_]  # neuronas: entrada, ocultas, salida
    pesos = sum(c.size for c in mlp.coefs_) + sum(b.size for b in mlp.intercepts_)   # pesos + sesgos aprendidos
    return capas, int(pesos)
