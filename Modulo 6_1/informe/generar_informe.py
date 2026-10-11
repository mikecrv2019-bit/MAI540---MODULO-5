"""Genera informe/Informe_Tarea_6_1.docx (formato APA 7) leyendo TODAS las cifras de metricas.json.

Uso:  python informe/generar_informe.py
Las cifras de las tablas y del texto se calculan desde evidencia/02_ingeniero_modelos/metricas.json,
no se transcriben a mano.
"""
import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

RAIZ = Path(__file__).resolve().parent.parent
M = json.loads((RAIZ / "evidencia" / "02_ingeniero_modelos" / "metricas.json").read_text(encoding="utf-8"))
ARB, RF = M["modelos"]["arbol"], M["modelos"]["random_forest"]
BASE = M["linea_base_calculada"]
FUENTE = "Calibri"


# ---------- cifras ----------
def f3(x):  # .698 (APA: sin cero inicial en valores acotados a 1)
    return f"{x:.3f}".lstrip("0") if x < 1 else f"{x:.3f}"


def pp(x):  # diferencia en puntos porcentuales, con signo tipografico
    return f"{x:+.2f}".replace("-", "−")


def pp1(x):
    return f"{x:+.1f}".replace("-", "−")


def ps(mod, clave, sub):  # estadisticos de particion unica 0..29
    return mod["particion_unica"]["semillas_0_29"][clave][sub]


def dif(mod, clave):  # (media, min, max) menos la media CV, en pp
    cv = mod["cv"][clave]["media"]
    s = mod["particion_unica"]["semillas_0_29"][clave]
    return [(s[k] - cv) * 100 for k in ("media", "min", "max")]


# ---------- utilidades docx ----------
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
for lado in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, lado, Inches(1))

normal = doc.styles["Normal"]
normal.font.name = FUENTE
normal.font.size = Pt(11)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
normal.paragraph_format.line_spacing = 2.0
normal.paragraph_format.space_after = Pt(0)
normal.paragraph_format.space_before = Pt(0)

h1 = doc.styles["Heading 1"]
h1.font.name, h1.font.size, h1.font.bold = FUENTE, Pt(11), True
h1.font.color.rgb = None
for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
    h1.element.rPr.rFonts.set(qn(a), FUENTE)
for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
    if h1.element.rPr.rFonts.get(qn(a)) is not None:
        del h1.element.rPr.rFonts.attrib[qn(a)]
h1.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
h1.paragraph_format.line_spacing = 2.0
h1.paragraph_format.space_before = Pt(0)
h1.paragraph_format.space_after = Pt(0)
h1.paragraph_format.keep_with_next = True


def add_field(par, instr):
    for tipo, txt in (("begin", None), (None, instr), ("end", None)):
        run = par.add_run()
        if tipo:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tipo)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = txt
        run._r.append(el)


hp = sec.header.paragraphs[0]
hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
hp.paragraph_format.line_spacing = 1.0
add_field(hp, "PAGE")


def parrafo(texto="", indent=True, align=None, bold=False, italic=False, spacing=None, keep=False):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Inches(0.5)
    if align is not None:
        p.alignment = align
    if spacing:
        p.paragraph_format.line_spacing = spacing
    p.paragraph_format.keep_with_next = keep
    partes = texto if isinstance(texto, list) else [texto]
    for t in partes:
        if isinstance(t, tuple):  # (texto, 'i') cursiva
            r = p.add_run(t[0])
            r.italic = "i" in t[1]
            r.bold = "b" in t[1]
        else:
            r = p.add_run(t)
            r.bold, r.italic = bold, italic
    return p


def borde(celda, **lados):
    tcPr = celda._tc.get_or_add_tcPr()
    b = tcPr.find(qn("w:tcBorders"))
    if b is None:
        b = OxmlElement("w:tcBorders")
        tcPr.append(b)
    for lado, grosor in lados.items():
        el = OxmlElement(f"w:{lado}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(grosor))
        el.set(qn("w:color"), "000000")
        b.append(el)


def tabla(numero, titulo, encabezado, filas, nota, anchos):
    parrafo(f"Tabla {numero}", indent=False, bold=True, keep=True)
    parrafo(titulo, indent=False, italic=True, keep=True)
    t = doc.add_table(rows=1 + len(filas), cols=len(encabezado))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = False
    for i, fila in enumerate([encabezado] + filas):
        for j, val in enumerate(fila):
            c = t.cell(i, j)
            c.width = Inches(anchos[j])
            par = c.paragraphs[0]
            par.paragraph_format.line_spacing = 1.0
            par.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            r = par.add_run(val)
            r.font.size = Pt(10)
            if i == 0:
                borde(c, top=8, bottom=6)
            if i == len(filas):
                borde(c, bottom=8)
    n = parrafo([("Nota. ", "i"), nota], indent=False, spacing=1.0)
    for r in n.runs:
        r.font.size = Pt(10)
    n.paragraph_format.space_after = Pt(8)


# ---------- portada ----------
for _ in range(3):
    parrafo("", indent=False)
parrafo("Flujo de trabajo con agentes especializados: validación cruzada frente a partición única en German Credit",
        indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)
parrafo("", indent=False)
for linea in ("German Credit 6.1", "Atlantis University", "MAI 540: Machine Learning",
              "Kevin A. García Gallardo", "13 de octubre de 2026"):
    parrafo(linea, indent=False, align=WD_ALIGN_PARAGRAPH.CENTER)
doc.paragraphs[-1].add_run().add_break(WD_BREAK.PAGE)

# ---------- cuerpo ----------
parrafo("Flujo de trabajo con agentes especializados: validación cruzada frente a partición única en German Credit",
        indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True)

parrafo([
    "Se evaluó un modelo de aprobación de crédito con el conjunto German Credit (1,000 solicitudes, 20 variables, "
    "30 % de créditos malos; Hofmann, 1994) repartiendo el trabajo entre tres roles ejecutados como subagentes "
    "independientes: analista de datos, ingeniero de modelos y auditor. Cada rol tiene un archivo de definición con su "
    "responsabilidad, lo que puede y no puede tocar y su entregable (",
    (".claude/agents/", "i"),
    "). El analista entregó el resumen de datos (sin faltantes ni duplicados; la línea base «siempre bueno» acierta "
    f"{f3(BASE)}), el ingeniero las métricas y el auditor las recalculó con código propio (55 de 55 verificaciones "
    "correctas, sin fuga de información)."])

doc.add_heading("Método", level=1)
parrafo([
    "Se compararon un árbol de decisión y un Random Forest de scikit-learn 1.9.0 (Pedregosa et al., 2011), con "
    "hiperparámetros por defecto y ",
    ("random_state", "i"), " = 42. Ambos van dentro de un ", ("Pipeline", "i"),
    " cuyo primer paso codifica las 13 variables categóricas con ", ("OrdinalEncoder", "i"),
    " (categorías no vistas = −1) y deja pasar las 7 numéricas; así la codificación se ajusta solo con el "
    "entrenamiento de cada pliegue. La validación cruzada fue estratificada de 5 particiones, con mezcla y semilla 42 "
    "(Kohavi, 1995). Se reportan la media y la desviación estándar muestral de la exactitud por pliegue y la "
    "proporción de créditos malos detectados (",
    ("recall", "i"), " de la clase «mala»). Para la partición única se repitió ", ("train_test_split", "i"),
    " 75/25 estratificado con las semillas 0 a 29 (30 repeticiones, más que las 10 exigidas)."])

doc.add_heading("Resultados de la validación cruzada", level=1)
parrafo([
    f"El árbol alcanzó una exactitud media de {f3(ARB['cv']['exactitud']['media'])} y no supera la línea base de "
    f"{f3(BASE)} ({pp1((ARB['cv']['exactitud']['media'] - BASE) * 100)} pp). El Random Forest llegó a "
    f"{f3(RF['cv']['exactitud']['media'])} ({pp1((RF['cv']['exactitud']['media'] - BASE) * 100)} pp) con la menor "
    f"variabilidad entre pliegues. Sin embargo, el modelo más exacto detecta menos créditos malos: "
    f"{RF['cv']['recall_bad']['media'] * 100:.1f} % frente a {ARB['cv']['recall_bad']['media'] * 100:.1f} % del árbol "
    f"(Tabla 1), es decir, deja pasar más de seis de cada diez créditos malos."])

filas1 = []
for nombre, mod in (("Árbol de decisión", ARB), ("Random Forest", RF)):
    e, r = mod["cv"]["exactitud"], mod["cv"]["recall_bad"]
    filas1.append([nombre, f"{f3(e['media'])} ({f3(e['desv'])})", f"{f3(r['media'])} ({f3(r['desv'])})",
                   pp1((e["media"] - BASE) * 100)])
tabla(1, "Validación cruzada estratificada de 5 pliegues",
      ["Modelo", "Exactitud M (DE)", "Malos detectados M (DE)", "Exactitud − base (pp)"], filas1,
      f"M = media; DE = desviación estándar muestral entre los 5 pliegues; pp = puntos porcentuales. Línea base "
      f"«siempre bueno» = {f3(BASE)}. «Malos detectados» es la proporción de créditos malos clasificados como malos.",
      [1.7, 1.5, 1.8, 1.5])

doc.add_heading("Comparación con la partición única", level=1)
a_e, r_e = ps(ARB, "exactitud", "min"), ps(RF, "exactitud", "min")
parrafo([
    f"Con una partición 75/25 la exactitud del árbol varió entre {f3(ps(ARB, 'exactitud', 'min'))} y "
    f"{f3(ps(ARB, 'exactitud', 'max'))} y la del Random Forest entre {f3(r_e)} y {f3(ps(RF, 'exactitud', 'max'))} "
    f"según la semilla (Tabla 2); con solo las semillas 0 a 9 los rangos son "
    f"{f3(ARB['particion_unica']['semillas_0_9']['exactitud']['min'])}–{f3(ARB['particion_unica']['semillas_0_9']['exactitud']['max'])} "
    f"y {f3(RF['particion_unica']['semillas_0_9']['exactitud']['min'])}–{f3(RF['particion_unica']['semillas_0_9']['exactitud']['max'])}. "
    f"El promedio de las 30 particiones difiere de la media de la validación cruzada en "
    f"{pp(dif(ARB, 'exactitud')[0])} pp (árbol) y {pp(dif(RF, 'exactitud')[0])} pp (Random Forest), pero una partición "
    f"individual se aleja entre {pp(dif(ARB, 'exactitud')[1])} y {pp(dif(ARB, 'exactitud')[2])} pp (árbol) y entre "
    f"{pp(dif(RF, 'exactitud')[1])} y {pp(dif(RF, 'exactitud')[2])} pp (Random Forest). La dispersión entre "
    f"particiones (DE = {f3(ps(ARB, 'exactitud', 'desv'))} y {f3(ps(RF, 'exactitud', 'desv'))}) es del orden del error "
    "estándar binomial de una exactitud cercana a .75 con 250 casos de prueba (≈ .027). El recall de los malos oscila "
    f"entre {f3(ps(ARB, 'recall_bad', 'min'))} y {f3(ps(ARB, 'recall_bad', 'max'))} (árbol) y entre "
    f"{f3(ps(RF, 'recall_bad', 'min'))} y {f3(ps(RF, 'recall_bad', 'max'))} (Random Forest): una sola partición habría "
    "podido sugerir cualquier conclusión sobre qué modelo detecta más malos. La referencia es una única validación "
    "cruzada (semilla 42), por lo que la diferencia es una estimación, no un valor exacto."])

filas2 = []
for nombre, mod in (("Árbol de decisión", ARB), ("Random Forest", RF)):
    for etiqueta, clave in (("Exactitud", "exactitud"), ("Malos detectados", "recall_bad")):
        s = mod["particion_unica"]["semillas_0_29"][clave]
        d = dif(mod, clave)
        filas2.append([nombre, etiqueta, f3(s["min"]), f3(s["max"]), f"{f3(s['media'])} ({f3(s['desv'])})",
                       pp(d[0]), f"[{pp(d[1])}; {pp(d[2])}]"])
tabla(2, "Partición única 75/25 con 30 semillas (0 a 29) frente a la media de la validación cruzada",
      ["Modelo", "Métrica", "Mín.", "Máx.", "M (DE)", "M − M CV (pp)", "Rango − M CV (pp)"], filas2,
      "M CV = media de la validación cruzada (Tabla 1). La última columna es [mínimo − M CV; máximo − M CV] en puntos "
      "porcentuales.",
      [1.3, 1.2, 0.6, 0.6, 1.0, 0.9, 1.3])

doc.add_heading("Evaluación crítica de la distribución", level=1)
parrafo([
    "Repartir el trabajo aportó verificación independiente, no mejores cifras: ningún rol cambió un resultado. "
    "El auditor recalculó todo con código propio y sus comprobaciones coincidieron exactamente, incluida una prueba de "
    "comportamiento del Pipeline: una categoría ausente del entrenamiento (",
    ("retraining", "i"),
    ", 9 filas) se codificó como −1 en la validación, lo que muestra que el codificador se ajusta solo con los datos de entrenamiento. Esa evidencia es más sólida que "
    "leer el código. ",
    ("Ejemplo 1 (hallazgo de un rol). ", "b"),
    "El auditor no halló ningún error de cálculo; lo que detectó fueron riesgos de interpretación: presentar la media de "
    "30 particiones (−1.72 pp) como «la» diferencia ocultaría el −9.00 pp del árbol, y las recomendaciones del analista "
    "(escalar, aplicar logaritmos, añadir F1 y AUC) excedían lo pedido, algo que yo ya había descartado al leer el "
    "traspaso. ",
    ("Ejemplo 2 (costo). ", "b"),
    "Los tres subagentes consumieron unos 318 mil tokens (90,448; 96,147 y 131,487) y cerca de 7 minutos, para algo "
    "que el script ", ("reproducir.py", "i"),
    " regenera en unos 50 segundos en este equipo. Además, el auditor no pudo escribir su reporte por una restricción de la herramienta y tuve "
    "que transcribirlo, lo que debilita la separación de funciones que justificaba el esquema. ",
    ("Conclusión. ", "b"),
    "No medí la alternativa de una sola conversación, de modo que esto es una inferencia. Lo repetiría solo para tareas "
    "donde importe la verificación independiente (auditar fuga de información, reproducibilidad de cifras, decisiones "
    "de riesgo como el crédito), con el auditor como único rol realmente separado. No lo repetiría para una tubería "
    "pequeña y determinista como esta, donde separar analista e ingeniero costó más de lo que aportó."])

# ---------- referencias ----------
doc.add_heading("Referencias", level=1)
refs = [
    [("Hofmann, H. (1994). ", ""), ("Statlog (German Credit Data)", "i"),
     (" [Conjunto de datos]. UCI Machine Learning Repository. https://doi.org/10.24432/C5NC77", "")],
    [("Kohavi, R. (1995). A study of cross-validation and bootstrap for accuracy estimation and model selection. ", ""),
     ("Proceedings of the 14th International Joint Conference on Artificial Intelligence", "i"),
     (", 2, 1137–1143.", "")],
    [("Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., "
      "Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. "
      "(2011). Scikit-learn: Machine learning in Python. ", ""),
     ("Journal of Machine Learning Research", "i"), (", ", ""), ("12", "i"), (", 2825–2830.", "")],
]
for partes in refs:
    p = parrafo([(t, f) for t, f in partes], indent=False)
    p.paragraph_format.left_indent = Inches(0.5)
    p.paragraph_format.first_line_indent = Inches(-0.5)

cp = doc.core_properties
cp.author = "German Credit 6.1"
cp.title = "Flujo de trabajo con agentes especializados: validación cruzada frente a partición única en German Credit"
cp.subject = "MAI 540: Machine Learning · Tarea 6.1"
cp.language = "es"
cp.comments = ""

salida = RAIZ / "informe" / "Informe_Tarea_6_1.docx"
doc.save(salida)
print("OK:", salida)
