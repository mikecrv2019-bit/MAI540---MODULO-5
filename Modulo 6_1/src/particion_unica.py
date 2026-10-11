"""Rol 2: particion unica 75/25 estratificada para las semillas 0..29."""
from sklearn.base import clone
from sklearn.metrics import accuracy_score, recall_score
from sklearn.model_selection import train_test_split

SEMILLAS = list(range(30))
TEST_SIZE = 0.25


def evaluar_particion(pipeline, X, y, semilla):
    """Ajusta el pipeline en el 75% y evalua en el 25% (stratify=y)."""
    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=TEST_SIZE, stratify=y, random_state=semilla
    )
    modelo = clone(pipeline).fit(X_tr, y_tr)
    pred = modelo.predict(X_te)
    return float(accuracy_score(y_te, pred)), float(recall_score(y_te, pred, pos_label=1))


def evaluar_semillas(pipeline, X, y, semillas=SEMILLAS):
    """Devuelve {semilla: {'exactitud':..., 'recall_bad':...}}."""
    out = {}
    for s in semillas:
        acc, rec = evaluar_particion(pipeline, X, y, s)
        out[int(s)] = {"exactitud": acc, "recall_bad": rec}
    return out
