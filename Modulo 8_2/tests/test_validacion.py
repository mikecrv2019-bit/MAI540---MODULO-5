"""Pruebas de la particion, la validacion cruzada y la ausencia de fuga de datos."""
import numpy as np
import pytest
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.preprocessing import StandardScaler

from datos import cargar_datos
from modelos import crear_modelos
from validacion import crear_cv, dividir, evaluar_cv


@pytest.fixture(scope="module")
def datos():
    return cargar_datos()


def test_particion_estratificada_y_sin_traslape(datos):
    """Entrenamiento y prueba no comparten filas y conservan la proporcion de cada clase (+-0.02)."""
    X, y = datos
    X_tr, X_te, y_tr, y_te = dividir(X, y)
    assert set(X_tr.index).isdisjoint(X_te.index)
    assert len(X_tr) + len(X_te) == len(X)
    for clase, p in y.value_counts(normalize=True).items():
        assert abs((y_tr == clase).mean() - p) < 0.02
        assert abs((y_te == clase).mean() - p) < 0.02


def test_escalado_se_ajusta_solo_con_entrenamiento(datos):
    """Sin fuga: el escalador del Pipeline aprende la media del entrenamiento, no la de todos los datos."""
    X, y = datos
    X_tr, _, y_tr, _ = dividir(X, y)
    modelo = crear_modelos()["regresion_logistica"].fit(X_tr, y_tr)
    escalador = modelo.named_steps["escalado"]
    assert isinstance(escalador, StandardScaler)
    assert np.allclose(escalador.mean_, X_tr.mean().to_numpy())
    assert not np.allclose(escalador.mean_, X.mean().to_numpy())


def test_validacion_cruzada_es_determinista_y_tiene_15_estimaciones(datos):
    """Misma semilla -> mismas cifras; 5 pliegues x 3 repeticiones = 15 estimaciones por modelo."""
    X, y = datos
    X_tr, _, y_tr, _ = dividir(X, y)
    modelo = crear_modelos()["regresion_logistica"]
    a = evaluar_cv(modelo, X_tr, y_tr, crear_cv())
    b = evaluar_cv(modelo, X_tr, y_tr, crear_cv())
    assert len(a["f1_macro_por_pliegue"]) == 15
    assert a["f1_macro_por_pliegue"] == b["f1_macro_por_pliegue"]
    assert a["f1_macro"]["desv"] > 0


def test_cv_que_no_cubre_todas_las_filas_falla_con_mensaje_claro(datos):
    """Un cv con 10 pliegues por repeticion deja la mitad de las filas sin prediccion fuera de pliegue: debe fallar, no producir un analisis de errores falso."""
    X, y = datos
    with pytest.raises(ValueError, match="no cubre todas las filas"):
        evaluar_cv(crear_modelos()["arbol"], X, y, RepeatedStratifiedKFold(n_splits=10, n_repeats=1, random_state=42))
