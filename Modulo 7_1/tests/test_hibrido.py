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
    texto = "La probabilidad es de 78% y se trata de una persona de más de 75 años."   # 75 no está en los datos
    problemas = verificar_explicacion(texto, DATOS, 0.78)
    assert any("75" in p for p in problemas)                                          # debe mencionar el 75


def test_detecta_tono_incoherente():
    texto = "La probabilidad es de 12%, lo cual es considerado alto."
    problemas = verificar_explicacion(texto, {"edad": 45}, 0.12)
    assert any("alto" in p for p in problemas)


def test_explicacion_segura_solo_cita_lo_permitido():
    texto = explicacion_segura(DATOS, 0.78)
    assert verificar_explicacion(texto, DATOS, 0.78) == []         # el texto de respaldo siempre pasa


def test_probabilidad_entre_cero_y_uno():
    predictor, X_pru, _ = entrenar_predictor()
    assert 0.0 <= probabilidad_malo(predictor, X_pru, 0) <= 1.0
