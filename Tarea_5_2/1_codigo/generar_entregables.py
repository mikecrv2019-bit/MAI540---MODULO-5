"""
Genera los dos PDF de la tarea K-Means a partir de evidencia/:
  - Interpretacion_Grupos.pdf (media página)
  - Propuesta_Capstone_Dilitio_Wine_Corp.pdf (una página)

    python generar_entregables.py
"""

from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

AQUI = Path(__file__).parent
EV = AQUI / "evidencia"
perfil = pd.read_csv(EV / "perfil_grupos.csv", index_col="grupo")
zper = pd.read_csv(EV / "perfil_grupos_z.csv", index_col="grupo")

CUERPO = ParagraphStyle("c", fontName="Times-Roman", fontSize=11, leading=14, spaceAfter=6)
TITULO = ParagraphStyle("t", parent=CUERPO, fontName="Times-Bold", fontSize=13, alignment=1, spaceAfter=10)
PREG = ParagraphStyle("p", parent=CUERPO, fontName="Times-Bold", spaceAfter=2)
NOTA = ParagraphStyle("n", parent=CUERPO, fontName="Times-Italic", fontSize=10)


def pdf(nombre, elementos):
    doc = SimpleDocTemplate(str(AQUI / nombre), pagesize=letter, leftMargin=inch, rightMargin=inch,
                            topMargin=0.8 * inch, bottomMargin=0.8 * inch)
    doc.build(elementos)


# --- Media página: interpretación de grupos ---------------------------------
VARS = {0: ["alcohol", "color_intensity", "proline"],
        1: ["color_intensity", "malic_acid", "flavanoids"],
        2: ["proline", "alcohol", "flavanoids"]}
TEXTO = {
    0: ("Vinos ligeros: tienen el alcohol, la intensidad de color y la prolina más bajos de los tres grupos.",
        "posicionarlos como línea de entrada o consumo joven, con precio acotado."),
    1: ("Vinos oscuros y ácidos, con los flavonoides más bajos y el color más intenso.",
        "revisar su proceso (acidez y extracción fenólica) o destinarlos a mezcla antes de venderlos como varietal."),
    2: ("Vinos de cuerpo alto: la prolina, el alcohol y los flavonoides más altos.",
        "reservarlos para la línea premium y priorizarlos en el canal de mayor margen."),
}
el = [Paragraph("Interpretación de grupos K-Means (k = 3), dataset wine", TITULO),
      Paragraph("Valores: media del grupo y, entre paréntesis, desviaciones estándar respecto a la media global. "
                "Las acciones son propuestas para Dilitio Wine Corp.", NOTA)]
for g in range(3):
    datos = ", ".join(f"{c} {perfil.loc[g, c]:.2f} ({zper.loc[g, c]:+.2f})" for c in VARS[g])
    el.append(Paragraph(
        f"<b>Grupo {g} (n = {int(perfil.loc[g, 'n'])}).</b> {TEXTO[g][0]} [{datos}]. "
        f"<b>Acción en Dilitio Wine Corp:</b> {TEXTO[g][1]}", CUERPO))
pdf("Interpretacion_Grupos.pdf", el)

# --- Una página: propuesta de capstone --------------------------------------
PREGUNTAS = [
    ("1. Problema de tu sector",
     "Dilitio Wine Corp necesita segmentar su producción de forma objetiva para decidir qué línea de producto "
     "corresponde a cada lote (entrada, revisión de proceso o premium). Hoy no tenemos datos que indiquen cómo se "
     "hace esa decisión; el piloto de esta tarea muestra que la química del vino ya separa tres perfiles."),
    ("2. Datos disponibles",
     "El dataset wine.csv del servidor: 178 muestras y 13 variables químicas numéricas (alcohol, ácido málico, "
     "flavonoides, intensidad de color, prolina, etc.), más la etiqueta cultivar usada solo para contraste. "
     "No disponemos de datos comerciales (precios, ventas, clientes); habría que obtenerlos de Dilitio Wine Corp."),
    ("3. Técnica prevista",
     "Estandarización, K-Means (k elegido con codo y silueta; en el piloto k = 3) y PCA para visualizar, "
     "expuestos como tools de un servidor MCP (segmentar_kmeans y ejecutar_pca) para que un asistente de IA "
     "los invoque con permisos acotados a la carpeta datasets/."),
    ("4. Criterios de éxito",
     "Propuestos (a validar con la empresa): (a) silueta igual o superior a la del piloto, 0.2849; (b) grupos "
     "estables al cambiar la semilla o remuestrear; (c) que un enólogo de Dilitio Wine Corp confirme que cada "
     "grupo es interpretable; (d) que cada grupo tenga una acción asignada y un responsable."),
    ("5. Limitaciones anticipadas",
     "Muestra pequeña (178 filas); silueta moderada (0.28), es decir, grupos que se traslapan; el PCA de 2 "
     "componentes conserva solo 55.41 % de la varianza, así que el gráfico no muestra todo; el dataset es "
     "público y no necesariamente representa los vinos de Dilitio Wine Corp; K-Means supone grupos "
     "esféricos y es sensible a la escala y a valores atípicos."),
]
el = [Paragraph("Propuesta de capstone: Dilitio Wine Corp", TITULO)]
for q, t in PREGUNTAS:
    el += [Paragraph(q, PREG), Paragraph(t, CUERPO)]
pdf("Propuesta_Capstone_Dilitio_Wine_Corp.pdf", el)
print("ok")
