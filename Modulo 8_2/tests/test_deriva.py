"""Pruebas de la deteccion de deriva y de la simulacion de degradacion."""
import numpy as np
import pytest

from datos import cargar_datos
from deriva import MIN_LOTES_KS, mensaje_deriva, reporte_deriva
from simular_degradacion import aplicar_escenario, simular


@pytest.fixture(scope="module")
def X():
    return cargar_datos()[0]


def test_sin_cambio_no_hay_alerta(X):
    """Dos mitades de los mismos datos no deben disparar la alerta (falsa alarma)."""
    r = reporte_deriva(X.iloc[::2], X.iloc[1::2])
    assert r["ks_aplicado"] and not r["alerta"]
    assert "Sin senales" in mensaje_deriva(r)


def test_un_sesgo_de_prolina_se_detecta_y_se_nombra(X):
    """Prolina +50 % (otro metodo de medicion) debe marcar justo esa variable."""
    nuevo = X.iloc[1::2].copy()
    nuevo["proline"] *= 1.5
    r = reporte_deriva(X.iloc[::2], nuevo)
    assert "proline" in r["variables_con_deriva"] and r["alerta"]
    assert "ALERTA" in mensaje_deriva(r)


def test_con_pocos_lotes_solo_se_mira_el_rango(X):
    """Con menos de MIN_LOTES_KS lotes no se aplica KS (no tendria potencia) y el reporte lo dice."""
    r = reporte_deriva(X, X.iloc[: MIN_LOTES_KS - 1])
    assert not r["ks_aplicado"] and all(v["p"] is None for v in r["variables"])


def test_cuenta_los_lotes_fuera_de_rango(X):
    """Un lote con dos variables por encima del maximo se cuenta una sola vez; sin lotes, se rechaza."""
    nuevo = X.iloc[:5].copy()
    nuevo.loc[nuevo.index[0], ["proline", "alcohol"]] = [9999.0, 99.0]
    r = reporte_deriva(X, nuevo)
    assert r["lotes_con_valores_fuera_de_rango"] == 1
    with pytest.raises(ValueError, match="No hay lotes"):
        reporte_deriva(X, X.iloc[:0])


def test_aplicar_escenario_no_toca_los_datos_originales_y_el_ruido_es_reproducible(X):
    """El sesgo multiplica solo la variable indicada; el mismo generador da el mismo ruido."""
    desv = X.std(ddof=1)
    original = X.copy()
    sesgado = aplicar_escenario(X, {"proline": 1.25}, 0.0, np.random.default_rng(0), desv)
    assert (X == original).all().all()
    assert sesgado["proline"].equals(X["proline"] * 1.25) and sesgado["alcohol"].equals(X["alcohol"])
    a = aplicar_escenario(X, {}, 0.5, np.random.default_rng(7), desv)
    b = aplicar_escenario(X, {}, 0.5, np.random.default_rng(7), desv)
    assert a.equals(b) and not a.equals(X)


def test_mas_ruido_baja_la_exactitud_y_sin_cambio_se_mantiene_alta():
    """La simulacion reproduce lo esperado: sin cambio ~0.98 y con ruido de 1 desviacion cae varios puntos."""
    r = simular(n_repartos=10)["escenarios"]
    assert r["sin cambio"]["exactitud_media"] > 0.95
    assert r["ruido 1.0 desv."]["exactitud_media"] < r["sin cambio"]["exactitud_media"] - 0.03
