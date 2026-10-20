"""Pruebas de la regla nueva 2: con probabilidad entre 30% y 60% el texto no puede llamar «alto» ni «bajo» al riesgo.

Cada prueba de rechazo falla con el verificador de clase (que solo revisa por debajo de 30% y por encima de 60%)
y pasa con la regla. Los textos 7 y 12 son salidas reales del modelo de lenguaje (evidencia/ejecucion_antes.txt).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))   # permite importar los módulos de la raíz
import verificador
from verificador import explicacion_segura, verificar_explicacion

DATOS = {"edad": 37, "duración (meses)": 18, "monto": 3612, "cuenta corriente": "saldo entre 0 y 200", "vivienda": "propia"}


# ---- Lo que la regla debe rechazar -------------------------------------------------------------------------------
def test_rechaza_riesgo_alto_con_probabilidad_media():
    """Real, solicitud 7: 36% descrito como «alto»."""
    texto = ("El modelo de riesgo de crédito sugiere una probabilidad de crédito malo del 36%, lo cual es alto para una persona "
             "con una edad de 37 años y una duración de 18 meses.")
    problemas = verificar_explicacion(texto, DATOS, 0.36)
    assert any("alto" in p and "30%" in p for p in problemas)


def test_rechaza_riesgo_alto_en_el_segundo_ejemplo_real():
    """Real, solicitud 12: 37% descrito como «alto»."""
    datos = {"edad": 43, "duración (meses)": 12, "monto": 4843, "cuenta corriente": "saldo negativo", "vivienda": "alquilada"}
    texto = ("El modelo de riesgo de crédito sugiere una probabilidad de crédito malo del 37%, lo cual es alto para una persona "
             "con una edad de 43 años y una duración de 12 meses.")
    assert verificar_explicacion(texto, datos, 0.37)


def test_rechaza_riesgo_bajo_con_probabilidad_media():
    texto = "La probabilidad de crédito malo es de 52%, es decir un riesgo bajo."
    problemas = verificar_explicacion(texto, {"edad": 45}, 0.52)
    assert any("bajo" in p for p in problemas)


@pytest.mark.parametrize("prob", [0.30, 0.45, 0.60])               # los extremos de la franja también cuentan
def test_la_franja_incluye_30_y_60(prob):
    texto = f"La probabilidad de crédito malo es de {prob:.0%}, lo cual es un riesgo alto."
    assert verificar_explicacion(texto, {"edad": 45}, prob)


def test_regla_conectada_a_verificar_explicacion():
    texto = "La probabilidad de crédito malo es de 41%, lo cual es alto."
    suelta = verificador.verificar_tono_medio(texto, 0.41)
    assert suelta and set(suelta) <= set(verificar_explicacion(texto, {"edad": 45}, 0.41))


# ---- Lo que la regla NO debe rechazar (falsos positivos) -----------------------------------------------------------
@pytest.mark.parametrize("texto", [
    "La probabilidad de crédito malo es de 41%, un riesgo medio.",
    "La probabilidad de crédito malo es de 41%, un riesgo moderado, ni alto ni bajo.",
    "La probabilidad de crédito malo es de 41% y el riesgo no es alto.",                   # negación verdadera
    "La probabilidad de crédito malo es de 41%; bajo estas condiciones, el análisis sigue.",  # «bajo» como preposición
    "La probabilidad de crédito malo es de 41% para un monto alto de 5000.",               # «alto» describe el monto
])
def test_no_rechaza_textos_correctos_en_la_franja(texto):
    assert verificador.verificar_tono_medio(texto, 0.41) == []


@pytest.mark.parametrize("prob", [0.299, 0.601])               # fuera de la franja la regla no actúa (lo cubre el verificador de clase)
def test_fuera_de_la_franja_no_actua(prob):
    assert verificador.verificar_tono_medio("La probabilidad es de 12%, lo cual es alto.", prob) == []


@pytest.mark.parametrize("prob", [0.30, 0.45, 0.60])
def test_el_texto_de_respaldo_pasa_en_la_franja(prob):
    assert verificar_explicacion(explicacion_segura(DATOS, prob), DATOS, prob) == []
