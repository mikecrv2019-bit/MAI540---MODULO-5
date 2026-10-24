"""Pruebas del analisis de errores por categoria con los 178 lotes."""
import math

import pytest

from datos import cargar_datos
from detalle_errores import (MODELO, errores_por_clase, errores_por_confianza, errores_por_grupo, explicar_errores,
                             intervalo_wilson, tabla_de_lotes)
from modelos import crear_modelos


@pytest.fixture(scope="module")
def datos_y_tabla():
    X, y = cargar_datos()
    return X, y, tabla_de_lotes(X, y, crear_modelos()[MODELO])


def test_intervalo_wilson_con_valores_conocidos():
    """0 errores en 10 casos no es 'error cero': el limite superior es ~0.278. Con 5 de 10 el intervalo es simetrico."""
    lo, hi = intervalo_wilson(0, 10)
    assert lo == 0.0 and hi == pytest.approx(0.2775, abs=1e-3)
    lo, hi = intervalo_wilson(5, 10)
    assert lo + hi == pytest.approx(1.0, abs=1e-9)
    assert all(math.isnan(v) for v in intervalo_wilson(0, 0))


def test_cada_lote_se_predice_una_vez_y_las_clases_suman_178(datos_y_tabla):
    """Los n por clase son los de los datos (59, 71, 48) y los errores por clase suman los errores de la tabla."""
    X, y, tabla = datos_y_tabla
    assert len(tabla) == len(X) == 178
    por_clase = errores_por_clase(tabla)
    assert [c["n"] for c in por_clase] == [59, 71, 48]
    assert sum(c["errores"] for c in por_clase) == int(tabla["error"].sum())
    assert (tabla["error"] == (tabla["real"] != tabla["predicho"])).all()


def test_confianza_es_una_probabilidad_valida(datos_y_tabla):
    """Con 3 clases la confianza (probabilidad de la clase predicha) va de 1/3 a 1."""
    _, _, tabla = datos_y_tabla
    assert tabla["confianza"].between(1 / 3 - 1e-9, 1.0).all()
    assert (tabla["prob_clase_real"] <= tabla["confianza"] + 1e-12).all()


def test_los_grupos_por_tercil_y_por_confianza_cubren_todos_los_lotes(datos_y_tabla):
    """Ningun lote se pierde ni se cuenta dos veces al agrupar."""
    X, _, tabla = datos_y_tabla
    for variable in ("alcohol", "proline"):
        assert sum(g["n"] for g in errores_por_grupo(tabla, X, variable)) == 178
    assert sum(g["n"] for g in errores_por_confianza(tabla)) == 178


def test_cada_error_tiene_su_explicacion_y_se_parece_mas_a_la_clase_predicha(datos_y_tabla):
    """Las variables citadas deben quedar mas cerca de la clase predicha que de la real (z menor)."""
    X, y, tabla = datos_y_tabla
    explicaciones = explicar_errores(X, y, tabla)
    assert len(explicaciones) == int(tabla["error"].sum())
    for e in explicaciones:
        assert e["real"] != e["predicho"]
        for d in e["variables_que_lo_acercan_a_la_clase_predicha"]:
            assert d["z_en_clase_predicha"] < d["z_en_clase_real"]
