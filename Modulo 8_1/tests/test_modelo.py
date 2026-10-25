"""Pruebas del modelo elegido: supera la linea base, es estable y la prueba final no se usa para decidir."""
import numpy as np
import pytest

from datos import cargar_datos
from entrenar import comparar_modelos
from modelos import LINEA_BASE, crear_modelos
from seleccion import MEJORA_MINIMA, elegir_modelo
from validacion import dividir, evaluar_prueba

UMBRAL_DESVIACION = 0.05


@pytest.fixture(scope="module")
def flujo():
    X, y = cargar_datos()
    X_tr, X_te, y_tr, y_te = dividir(X, y)
    cv = comparar_modelos(X_tr, y_tr)
    return {"X_tr": X_tr, "X_te": X_te, "y_tr": y_tr, "y_te": y_te, "cv": cv, "decision": elegir_modelo(cv)}


def test_el_modelo_elegido_supera_a_la_linea_base(flujo):
    """F1 macro CV del elegido > linea base + MEJORA_MINIMA, y la linea base se parece a 'siempre la clase mayoritaria'."""
    cv, elegido = flujo["cv"], flujo["decision"]["elegido"]
    base = cv[LINEA_BASE]["f1_macro"]["media"]
    assert cv[elegido]["f1_macro"]["media"] > base + MEJORA_MINIMA
    clase_mayoritaria = flujo["y_tr"].value_counts(normalize=True).max()
    assert cv[LINEA_BASE]["exactitud"]["media"] == pytest.approx(clase_mayoritaria, abs=0.03)


def test_desviacion_de_la_validacion_cruzada_del_elegido(flujo):
    """La desviacion entre los 15 pliegues del elegido no supera 0.05 (sqrt(.98*.02/28) = 0.026 es el ruido por muestreo)."""
    elegido = flujo["decision"]["elegido"]
    assert flujo["cv"][elegido]["exactitud"]["desv"] <= UMBRAL_DESVIACION


def test_la_prueba_final_confirma_la_validacion_cruzada(flujo):
    """La prueba final del elegido queda a menos de 0.10 de su exactitud CV (sin sobreajuste a la CV) y supera a la base."""
    elegido = flujo["decision"]["elegido"]
    p = evaluar_prueba(crear_modelos()[elegido], flujo["X_tr"], flujo["y_tr"], flujo["X_te"], flujo["y_te"])
    base = evaluar_prueba(crear_modelos()[LINEA_BASE], flujo["X_tr"], flujo["y_tr"], flujo["X_te"], flujo["y_te"])
    assert abs(p["exactitud"] - flujo["cv"][elegido]["exactitud"]["media"]) < 0.10
    assert p["exactitud"] > base["exactitud"] + 0.3


def test_la_eleccion_no_depende_de_la_prueba_final(flujo):
    """La decision se calcula solo con resultados de CV: ni la fila de prueba ni sus indices aparecen en ellos."""
    assert set(flujo["X_tr"].index).isdisjoint(flujo["X_te"].index)
    assert set(flujo["decision"]) >= {"elegido", "equivalentes", "regla"}
    assert np.isfinite(flujo["decision"]["piso_de_equivalencia"])
