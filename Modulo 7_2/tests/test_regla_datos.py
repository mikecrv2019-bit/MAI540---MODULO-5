"""Pruebas de la regla nueva 1: el texto no puede contradecir los datos de la solicitud (cuenta corriente, vivienda).

Cada prueba que busca un rechazo falla con el verificador de clase (que nunca compara el texto con los datos)
y pasa con la regla. Los textos 3, 4 y 8 son salidas reales del modelo de lenguaje (evidencia/ejecucion_antes.txt).
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))   # permite importar los módulos de la raíz
import verificador                                                  # la regla suelta se llama como verificador.verificar_datos
from verificador import explicacion_segura, verificar_explicacion

DATOS = {"edad": 25, "duración (meses)": 48, "monto": 5951, "cuenta corriente": "saldo negativo", "vivienda": "alquilada"}


# ---- Lo que la regla debe rechazar -------------------------------------------------------------------------------
def test_rechaza_cuenta_corriente_contradicha():
    """Real, solicitud 8: el texto dice «sin saldo negativo» y el dato es «saldo negativo»."""
    datos = {"edad": 23, "duración (meses)": 6, "monto": 1352, "cuenta corriente": "saldo negativo", "vivienda": "alquilada"}
    texto = ("El modelo de riesgo de crédito sugiere una probabilidad de crédito malo del 43%, lo cual es alto para una persona "
             "con una edad de 23 años y una duración de 6 meses en una cuenta corriente sin saldo negativo.")
    problemas = verificar_explicacion(texto, datos, 0.78)           # 0.78 aísla esta regla: fuera de la franja 30-60%
    assert any("saldo negativo" in p for p in problemas)


def test_rechaza_saldo_afirmado_que_no_es_el_dato():
    texto = "La probabilidad es de 78%, porque la cuenta corriente tiene un saldo negativo."
    datos = {**DATOS, "cuenta corriente": "saldo entre 0 y 200"}
    assert any("cuenta corriente" in p for p in verificar_explicacion(texto, datos, 0.78))


def test_rechaza_vivienda_contradicha():
    texto = "La probabilidad es de 78%, aunque el solicitante vive en una vivienda propia."
    problemas = verificar_explicacion(texto, DATOS, 0.78)           # el dato dice «alquilada»
    assert any("vivienda" in p for p in problemas)


def test_rechaza_atributo_que_no_esta_en_los_datos():
    """Real, solicitud 4: «persona sola» no tiene ningún dato que lo respalde."""
    datos = {"edad": 31, "duración (meses)": 18, "monto": 3104, "cuenta corriente": "saldo negativo", "vivienda": "propia"}
    texto = "La probabilidad es de 78%, ya que la cuenta corriente tiene un saldo negativo y la persona es una persona sola."
    assert any("persona sola" in p for p in verificar_explicacion(texto, datos, 0.78))


def test_regla_conectada_a_verificar_explicacion():
    """La regla suelta y el verificador completo deben coincidir en lo que señalan."""
    texto = "La probabilidad es de 78%, en una cuenta corriente sin saldo negativo."
    assert verificador.verificar_datos(texto, DATOS) and set(verificador.verificar_datos(texto, DATOS)) <= set(verificar_explicacion(texto, DATOS, 0.78))


# ---- Lo que la regla NO debe rechazar (falsos positivos) -----------------------------------------------------------
@pytest.mark.parametrize("texto", [
    "La probabilidad es de 78%, con una cuenta corriente de saldo negativo y vivienda alquilada.",   # coincide con el dato
    "La probabilidad es de 78%: el solicitante alquila y su saldo es negativo.",
    "La probabilidad es de 78%, aunque no es propietario de su vivienda.",                            # negación verdadera
    "La probabilidad es de 78% y el monto es de 5951.",                                              # no habla de cuenta ni vivienda
])
def test_no_rechaza_textos_que_coinciden_con_los_datos(texto):
    assert verificador.verificar_datos(texto, DATOS) == []


def test_sin_los_campos_no_inventa_problemas():
    """Con datos incompletos (como en la prueba original del tono) la regla no falla ni rechaza."""
    assert verificador.verificar_datos("La probabilidad es de 12%.", {"edad": 45}) == []


@pytest.mark.parametrize("cuenta", ["saldo negativo", "saldo entre 0 y 200", "saldo de 200 o más", "sin cuenta corriente"])
@pytest.mark.parametrize("vivienda", ["propia", "alquilada", "sin costo"])
@pytest.mark.parametrize("prob", [0.05, 0.45, 0.85])
def test_el_texto_de_respaldo_siempre_pasa(cuenta, vivienda, prob):
    datos = {**DATOS, "cuenta corriente": cuenta, "vivienda": vivienda}
    assert verificar_explicacion(explicacion_segura(datos, prob), datos, prob) == []
