"""Pruebas automáticas de la capa de verificación y del predictor. Se ejecutan con:  pytest -v"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))   # permite importar los módulos de la raíz
from predictor import entrenar_predictor, probabilidad_malo
from verificador import explicacion_segura, verificar_explicacion

DATOS = {"edad": 25, "duración (meses)": 48, "monto": 5951, "cuenta corriente": "saldo negativo", "vivienda": "alquilada"}


def test_texto_correcto_pasa():
    texto = "El modelo estima 78% de probabilidad de crédito malo, por la duración de 48 meses y el saldo negativo."
    assert verificar_explicacion(texto, DATOS, 0.78) == []         # no debe señalar nada


def test_detecta_un_dato_inventado():
    # TODO 10 (en clase): un texto con un número inventado debe ser rechazado
    raise NotImplementedError("TODO 10: completar en clase")


def test_detecta_tono_incoherente():
    # TODO 11 (en clase): dice «alto» con una probabilidad baja
    raise NotImplementedError("TODO 11: completar en clase")


def test_explicacion_segura_solo_cita_lo_permitido():
    texto = explicacion_segura(DATOS, 0.78)
    assert verificar_explicacion(texto, DATOS, 0.78) == []         # el texto de respaldo siempre pasa


def test_probabilidad_entre_cero_y_uno():
    predictor, X_pru, _ = entrenar_predictor()
    assert 0.0 <= probabilidad_malo(predictor, X_pru, 0) <= 1.0
