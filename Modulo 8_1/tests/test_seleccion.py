"""Pruebas del criterio de seleccion con resultados sinteticos (el criterio es una regla, no un resultado)."""
import pytest

from seleccion import MEJORA_MINIMA, elegir_modelo


def _res(base, **modelos):
    r = {"linea_base": {"f1_macro": {"media": base, "desv": 0.0}}}
    for nombre, (media, desv) in modelos.items():
        r[nombre] = {"f1_macro": {"media": media, "desv": desv}}
    return r


def test_elige_el_mas_simple_entre_equivalentes():
    """Dentro de 1 desviacion del mejor gana el modelo mas simple, aunque no tenga la media mas alta."""
    res = _res(0.20, regresion_logistica=(0.97, 0.02), random_forest=(0.98, 0.02), boosting=(0.985, 0.02))
    d = elegir_modelo(res)
    assert d["mejor_por_media"] == "boosting"
    assert d["elegido"] == "regresion_logistica"


def test_no_elige_un_modelo_fuera_de_la_desviacion_del_mejor():
    """Si el simple queda mas de 1 desviacion abajo, se elige uno mas complejo."""
    res = _res(0.20, regresion_logistica=(0.80, 0.02), random_forest=(0.95, 0.02))
    assert elegir_modelo(res)["elegido"] == "random_forest"


def test_descarta_modelos_que_no_superan_la_linea_base():
    """Un modelo que no mejora a la linea base por MEJORA_MINIMA no puede ser elegido; si ninguno, error."""
    res = _res(0.50, arbol=(0.50 + MEJORA_MINIMA - 0.01, 0.01), random_forest=(0.90, 0.02))
    d = elegir_modelo(res)
    assert d["elegido"] == "random_forest"
    assert d["descartados_por_linea_base"] == ["arbol"]
    with pytest.raises(ValueError, match="Ningun modelo supera"):
        elegir_modelo(_res(0.50, arbol=(0.52, 0.01)))
