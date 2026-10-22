"""Pruebas de la carga y validacion de datos."""
import numpy as np
import pytest

from datos import CLASES, OBJETIVO, PREDICTORAS, cargar_datos, validar_datos


def test_forma_de_los_datos_y_objetivo_fuera_de_X():
    """178 lotes, 13 predictoras, y la etiqueta no esta entre las predictoras."""
    X, y = cargar_datos()
    assert X.shape == (178, 13)
    assert OBJETIVO not in X.columns
    assert list(X.columns) == PREDICTORAS
    assert set(y.unique()) == set(CLASES)


def test_validar_rechaza_nan_y_columna_faltante():
    """Datos con NaN o sin una columna deben fallar con ValueError, no pasar en silencio."""
    X, y = cargar_datos()
    df = X.assign(**{OBJETIVO: y})
    con_nan = df.copy()
    con_nan.loc[0, "alcohol"] = np.nan
    with pytest.raises(ValueError, match="NaN"):
        validar_datos(con_nan)
    with pytest.raises(ValueError, match="Faltan columnas"):
        validar_datos(df.drop(columns=["proline"]))
