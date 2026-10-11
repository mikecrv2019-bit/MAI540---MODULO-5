"""Pruebas automaticas de la Tarea 6.2. Si fallan, el cambio no se acepta.  Ejecutar:  pytest -v

Las pruebas 1 y 2 evaluan el MODELO ELEGIDO (src/config.py) con la misma validacion cruzada del informe.
"""
import json

import numpy as np
import pandas as pd
import pytest

from auditoria import MIN_POSITIVOS, recall_por_subgrupo
from busqueda import PARAM_GRID
from config import MODELO_ELEGIDO
from curvas_auditoria import modelo_elegido
from datos import RAIZ, VARIABLES_SENSIBLES, cargar_datos, predictoras
from modelos import crear_pipeline, estimadores_base
from validacion import crear_cv, evaluar, linea_base_siempre_bueno

UMBRAL_DESVIACION = 0.05


@pytest.fixture(scope="module")
def datos():
    X_todas, y = cargar_datos()
    return predictoras(X_todas), y


@pytest.fixture(scope="module")
def evaluacion_elegido(datos):
    """Validacion cruzada del modelo elegido (una sola vez para todo el modulo)."""
    X, y = datos
    return evaluar(modelo_elegido(X), X, y, crear_cv())


def test_supera_a_siempre_bueno(datos, evaluacion_elegido):
    """El modelo elegido debe acertar mas que predecir siempre 'good' (0.70)."""
    _, y = datos
    base = linea_base_siempre_bueno(y)
    assert base == pytest.approx(0.70)
    media = float(np.mean(evaluacion_elegido["exactitud_por_pliegue"]))
    assert media > base, f"{MODELO_ELEGIDO}: exactitud CV {media:.4f} no supera la linea base {base:.2f}"


def test_desviacion_de_la_validacion_cruzada(evaluacion_elegido):
    """La desviacion entre pliegues no debe superar 0.05.

    Justificacion del umbral: con 200 casos por pliegue y una exactitud cercana a 0.70, el error estandar
    puramente muestral es sqrt(0.70 * 0.30 / 200) = 0.032. Un umbral de 0.05 (~1.5 veces ese ruido) deja pasar la
    variacion esperada por azar y detecta un modelo inestable. Con el mismo criterio el arbol afinado (DE .033) pasa
    por poco, mientras que su recall de 'bad' (DE .115) delata la inestabilidad que la exactitud no muestra.
    """
    desv = float(np.std(evaluacion_elegido["exactitud_por_pliegue"], ddof=1))
    assert desv <= UMBRAL_DESVIACION, f"DE entre pliegues = {desv:.4f} > {UMBRAL_DESVIACION}"


def test_variables_sensibles_no_son_predictoras(datos):
    """Las variables sensibles se usan para auditar, no para decidir: no estan en X."""
    X, _ = datos
    assert set(VARIABLES_SENSIBLES).isdisjoint(X.columns)
    assert X.shape[1] == 18


def test_codificacion_dentro_del_pipeline(datos):
    """La codificacion es un paso del Pipeline (se ajusta por pliegue, sin fuga) y el modelo recibe X sin transformar."""
    X, _ = datos
    pipe = crear_pipeline(estimadores_base()[MODELO_ELEGIDO if MODELO_ELEGIDO != "arbol_afinado" else "arbol_defecto"], X)
    assert list(pipe.named_steps) == ["prep", "modelo"]
    assert X.select_dtypes(include=["object", "string"]).shape[1] == 12  # 13 categoricas menos personal_status; siguen como texto en X


def test_pipelines_no_comparten_estimador(datos):
    """Regresion: fijar parametros en un Pipeline no debe cambiar a otro (error encontrado al reconstruir la curva)."""
    X, _ = datos
    base = estimadores_base()["arbol_defecto"]
    a, b = crear_pipeline(base, X), crear_pipeline(base, X)
    a.set_params(modelo__max_depth=3)
    assert b.get_params()["modelo__max_depth"] is None and base.get_params()["max_depth"] is None


def test_es_reproducible(datos):
    """Misma semilla, mismas predicciones fuera de pliegue."""
    X, y = datos
    p1 = evaluar(crear_pipeline(estimadores_base()["boosting_hgb"], X), X, y, crear_cv())["prediccion_fuera_de_pliegue"]
    p2 = evaluar(crear_pipeline(estimadores_base()["boosting_hgb"], X), X, y, crear_cv())["prediccion_fuera_de_pliegue"]
    assert np.array_equal(p1, p2)


def test_la_busqueda_explora_al_menos_dos_hiperparametros():
    assert len(PARAM_GRID) >= 2 and all(len(v) > 1 for v in PARAM_GRID.values())


def test_evidencia_consistente_con_la_matriz():
    """Las cifras guardadas coinciden con la matriz de confusion (exactitud y recall, tolerancia 0.001)."""
    ruta = RAIZ / "evidencia" / "busqueda_comparacion.json"
    if not ruta.exists():
        pytest.skip("falta evidencia/busqueda_comparacion.json: correr src/reproducir.py")
    comp = json.loads(ruta.read_text(encoding="utf-8"))["comparacion"]
    for nombre in ("arbol_defecto", "arbol_afinado", "random_forest", "boosting_hgb"):
        m = comp[nombre]
        mx = m["matriz_fuera_de_pliegue"]
        assert abs(mx["exactitud"] - m["exactitud"]["media"]) <= 0.001, nombre
        assert abs(mx["recall_bad"] - m["recall_bad"]["media"]) <= 0.001, nombre


def test_recall_por_subgrupo_con_ejemplo_calculado_a_mano():
    """Subgrupo A: 4 'bad', el modelo acierta 3 -> recall 0.75. Subgrupo B: 2 'bad', acierta 1 -> 0.50."""
    y = pd.Series([1, 1, 1, 1, 0, 1, 1, 0])
    pred = np.array([1, 1, 1, 0, 0, 1, 0, 0])
    grupos = pd.DataFrame({"g": ["A", "A", "A", "A", "A", "B", "B", "B"]})
    tabla, global_ = recall_por_subgrupo(y, pred, grupos, "g")
    assert global_ == pytest.approx(4 / 6)  # 4 aciertos de 6 'bad'
    a = tabla.set_index("valor").loc["A"]
    assert a.positivos_bad == 4 and a.recall_bad == pytest.approx(0.75) and not a.evaluable  # < MIN_POSITIVOS
    assert MIN_POSITIVOS == 20
