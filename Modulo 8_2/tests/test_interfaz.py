"""Pruebas de la demostracion: clasificar un lote o un archivo, entradas invalidas y la pantalla."""
import pytest

from datos import PREDICTORAS, RUTA_DATOS, cargar_datos
from interfaz import EJEMPLOS, evaluar_archivo, evaluar_lote, leer_archivo, valores_de_ejemplo, valores_tipicos


def test_un_lote_tipico_se_clasifica_con_confianza_alta():
    """El lote 0 es class_0: perfil correcto, probabilidades que suman 1 y ningun aviso de confianza baja."""
    prob, texto = evaluar_lote(valores_de_ejemplo("Lote típico class_0"))
    assert max(prob, key=prob.get) == "class_0" and sum(prob.values()) == pytest.approx(1.0, abs=1e-3)
    assert "Confianza baja" not in texto


def test_un_lote_ambiguo_avisa_de_confianza_baja():
    """El lote 83 es el caso dificil de la validacion: la confianza queda bajo 80 % y se pide revisarlo."""
    prob, texto = evaluar_lote(valores_de_ejemplo("Lote ambiguo (el 83)"))
    assert max(prob.values()) < 0.80
    assert "Confianza baja" in texto


def test_una_entrada_vacia_no_rompe_la_pantalla():
    """Un campo vacio (None) devuelve un mensaje, no una excepcion."""
    valores = valores_tipicos()
    valores[4] = None
    prob, texto = evaluar_lote(valores)
    assert prob == {} and "No se pudo clasificar" in texto


def test_un_valor_fuera_de_rango_se_advierte():
    """Una prolina de 5000 (el maximo del entrenamiento es 1680) clasifica igual, pero avisa."""
    valores = valores_tipicos()
    valores[PREDICTORAS.index("proline")] = 5000.0
    _, texto = evaluar_lote(valores)
    assert "Fuera de rango" in texto


def test_el_archivo_se_valida_con_mensajes_claros(tmp_path):
    """Falta una columna, hay un texto en una medicion o el archivo esta vacio: se rechaza con el motivo."""
    X, _ = cargar_datos()
    sin_prolina = tmp_path / "a.csv"
    X.drop(columns="proline").to_csv(sin_prolina, index=False)
    with pytest.raises(ValueError, match="Faltan columnas"):
        leer_archivo(sin_prolina)
    con_texto = tmp_path / "b.csv"
    malo = X.astype(object).copy()
    malo.iloc[3, 0] = "mucho"
    malo.to_csv(con_texto, index=False)
    with pytest.raises(ValueError, match="no son números"):
        leer_archivo(con_texto)
    vacio = tmp_path / "c.csv"
    vacio.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="No pude leer"):
        leer_archivo(vacio)


def test_el_archivo_completo_da_exactitud_alta_y_sin_alerta():
    """El archivo de datos mismo: 178 lotes con las columnas del resultado y sin senales de deriva."""
    tabla, resumen = evaluar_archivo(RUTA_DATOS)
    assert len(tabla) == 178 and {"perfil", "confianza", "revisar"} <= set(tabla.columns)
    assert "Sin senales de deriva" in resumen and "exactitud" in resumen


def test_un_archivo_con_la_prolina_desplazada_dispara_la_alerta(tmp_path):
    """Si el laboratorio cambia el metodo y la prolina sube 50 %, el control de deriva lo avisa."""
    X, y = cargar_datos()
    X["proline"] *= 1.5
    X["cultivar"] = y
    ruta = tmp_path / "desplazado.csv"
    X.to_csv(ruta, index=False)
    tabla, resumen = evaluar_archivo(ruta)
    assert "ALERTA" in resumen and "proline" in resumen
    assert (tabla["perfil"] == tabla["cultivar"]).mean() < 0.99


def test_la_pantalla_se_construye_con_todos_los_campos():
    """app_gradio.construir() arma la pantalla con 13 campos numericos y un boton por lote de ejemplo."""
    gr = pytest.importorskip("gradio")
    import app_gradio
    demo = app_gradio.construir()
    campos = [b for b in demo.blocks.values() if isinstance(b, gr.Number)]
    botones = [b.value for b in demo.blocks.values() if isinstance(b, gr.Button)]
    assert len(campos) == len(PREDICTORAS)
    assert set(EJEMPLOS) <= set(botones)
