"""Pruebas de la herramienta de uso: entradas invalidas, advertencias de rango y consistencia con los datos."""
import pytest

from datos import cargar_datos
from entrenar import RUTA_MODELO, ejecutar
from predecir import clasificar_lote


@pytest.fixture(scope="module")
def lote_base():
    if not RUTA_MODELO.exists():  # un clon limpio no trae el modelo: se entrena una vez
        ejecutar()
    X, y = cargar_datos()
    return {c: float(v) for c, v in X.iloc[0].items()}, y.iloc[0]


def test_clasifica_un_lote_valido(lote_base):
    """Un lote real devuelve su perfil, probabilidades que suman 1 y ninguna advertencia."""
    lote, real = lote_base
    r = clasificar_lote(lote)
    assert r["perfil"] == real
    assert sum(r["probabilidades"].values()) == pytest.approx(1.0, abs=1e-3)
    assert r["advertencias"] == []


def test_rechaza_lotes_incompletos_o_con_valores_invalidos(lote_base):
    """Falta de variable, variable extra, NaN y texto deben fallar con ValueError, no predecir en silencio."""
    lote, _ = lote_base
    sin_prolina = {k: v for k, v in lote.items() if k != "proline"}
    with pytest.raises(ValueError, match="Faltan"):
        clasificar_lote(sin_prolina)
    with pytest.raises(ValueError, match="Sobran"):
        clasificar_lote({**lote, "precio": 10.0})
    with pytest.raises(ValueError, match="numero finito"):
        clasificar_lote({**lote, "alcohol": float("nan")})
    with pytest.raises(ValueError, match="numero finito"):
        clasificar_lote({**lote, "alcohol": "14.2"})


def test_advierte_si_un_valor_sale_del_rango_de_entrenamiento(lote_base):
    """Un lote con prolina muy por encima del maximo se clasifica pero con advertencia de extrapolacion."""
    lote, _ = lote_base
    r = clasificar_lote({**lote, "proline": 20000.0})
    assert any("proline" in a for a in r["advertencias"])


def test_el_servidor_mcp_registra_las_dos_tools():
    """El servidor MCP importa y expone clasificar_lote y resumen_validacion (se omite si 'mcp' no esta instalado)."""
    pytest.importorskip("mcp")
    import mcp_server
    assert callable(mcp_server.clasificar_lote) and callable(mcp_server.resumen_validacion)


def test_la_tool_mcp_devuelve_el_motivo_cuando_el_lote_es_invalido():
    """Un cliente MCP solo veria 'Error executing tool'; la tool debe devolver el motivo del rechazo."""
    pytest.importorskip("mcp")
    import mcp_server
    r = mcp_server.clasificar_lote({"alcohol": 14.0})
    assert "Faltan" in r["error"]
