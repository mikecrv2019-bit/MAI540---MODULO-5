"""Demostración ejecutable: clasificador de perfil químico de lotes de vino (Dilitio Wine Corp), con interfaz web (Gradio).

Uso:   python app_gradio.py      y abra la dirección que aparece (http://127.0.0.1:7860)
La primera vez entrena el modelo (unos segundos). La lógica está en src/interfaz.py; aquí solo está la pantalla.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import gradio as gr  # noqa: E402

from datos import PREDICTORAS  # noqa: E402
from interfaz import (ETIQUETAS, EJEMPLOS, UMBRAL_CONFIANZA, asegurar_modelo, evaluar_archivo, evaluar_lote,  # noqa: E402
                      valores_de_ejemplo, valores_tipicos)

LIMITACIONES = f"""
**Antes de usar esta herramienta**

- Describe a qué **perfil químico** (`class_0`, `class_1`, `class_2`) se parece un lote. **No decide** la línea de producto ni
  la calidad: esa correspondencia la debe definir la empresa con un enólogo.
- Se entrenó con **178 muestras públicas** (UCI Wine, tres cultivares). No la use con vinos de otras regiones, uvas o métodos de
  laboratorio. Con **confianza menor a {UMBRAL_CONFIANZA:.0%}** o valores fuera de rango, trate el resultado como no confiable.
- No avisa sola cuando el mundo cambia. Para vigilarlo, suba un archivo de lotes en la segunda pestaña.
"""


def clasificar(*valores):
    return evaluar_lote(list(valores))


def clasificar_archivo(ruta):
    if ruta is None:
        return None, "Suba un archivo CSV."
    return evaluar_archivo(ruta)


def construir():
    asegurar_modelo()
    tipicos = valores_tipicos()
    with gr.Blocks(title="Perfil químico de lotes de vino · demostración") as demo:
        gr.Markdown("# Perfil químico de lotes de vino · Dilitio Wine Corp\n"
                    "Indique las 13 mediciones de laboratorio de un lote y vea a qué perfil químico se parece.")
        gr.Markdown(LIMITACIONES)
        with gr.Tab("Un lote"):
            with gr.Row():
                botones = {nombre: gr.Button(nombre, size="sm") for nombre in EJEMPLOS}
            campos = []
            for fila in range(0, len(PREDICTORAS), 4):
                with gr.Row():
                    for c, v in zip(PREDICTORAS[fila:fila + 4], tipicos[fila:fila + 4]):
                        campos.append(gr.Number(value=v, label=ETIQUETAS[c]))
            enviar = gr.Button("Clasificar lote", variant="primary")
            with gr.Row():
                probabilidades = gr.Label(label="Probabilidad por perfil", num_top_classes=3)
                texto = gr.Markdown()
            enviar.click(clasificar, inputs=campos, outputs=[probabilidades, texto])
            for nombre, boton in botones.items():
                boton.click(lambda n=nombre: valores_de_ejemplo(n), outputs=campos)
        with gr.Tab("Archivo de lotes y control de deriva"):
            gr.Markdown("Suba un CSV con las 13 columnas del archivo `datos/wine.csv` (puede incluir `cultivar` si conoce "
                        "el perfil real: así se mide la exactitud). Se clasifican todos los lotes y se compara su distribución "
                        "con la del entrenamiento.")
            archivo = gr.File(label="Archivo CSV", file_types=[".csv"], type="filepath")
            evaluar = gr.Button("Evaluar archivo", variant="primary")
            resumen = gr.Markdown()
            tabla = gr.Dataframe(label="Resultados por lote")
            evaluar.click(clasificar_archivo, inputs=archivo, outputs=[tabla, resumen])
    return demo


if __name__ == "__main__":
    construir().launch()
