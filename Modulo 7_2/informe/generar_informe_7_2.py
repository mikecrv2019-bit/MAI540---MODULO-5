"""Genera informe/Informe_Tarea_7_2.docx (formato APA 7, 3 páginas).

Uso:  python informe/generar_informe_7_2.py
Las cifras no se transcriben a mano: se leen de evidencia/comparacion_modelos.txt (python comparar_modelos.py),
de evidencia/textos_generados.json + evidencia/etiquetas.json (python main.py 200) y de medir_efecto.py.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from medir_efecto import MOTIVOS, medir, motivos            # noqa: E402

AUTOR = "Jaime Lopez"
FUENTE = "Calibri"
INTERLINEADO = 1.1

# ---------- cifras ----------
cmp_txt = (RAIZ / "evidencia" / "comparacion_modelos.txt").read_text(encoding="utf-8")


def num(patron):
    return float(re.search(patron, cmp_txt, re.S).group(1))


M = dict(
    base=num(r"siempre «bueno»: ([\d.]+)"), pesos=re.search(r"pesos aprendidos: ([\d,]+)", cmp_txt).group(1),
    nodos=re.search(r"([\d,]+) nodos", cmp_txt).group(1),
    red_ent=num(r"Red neuronal\s+capas.*?\n\s+exactitud ENTRENAMIENTO ([\d.]+)"), red_pru=num(r"Red neuronal\s+capas.*?PRUEBA ([\d.]+)"),
    red_det=num(r"Red neuronal\s+capas.*?malos detectados ([\d.]+)"),
    rf_ent=num(r"Random Forest.*?\n\s+exactitud ENTRENAMIENTO ([\d.]+)"), rf_pru=num(r"Random Forest.*?PRUEBA ([\d.]+)"),
    rf_det=num(r"Random Forest.*?malos detectados ([\d.]+)"),
    red_cv=num(r"Red neuronal\s+exactitud ([\d.]+) ±"), red_cv_sd=num(r"Red neuronal\s+exactitud [\d.]+ ± ([\d.]+)"),
    rf_cv=num(r"Random Forest\s+exactitud ([\d.]+) ±"), rf_cv_sd=num(r"Random Forest\s+exactitud [\d.]+ ± ([\d.]+)"),
)
M["red_cv_det"] = num(r"Red neuronal\s+exactitud [\d.]+ ± [\d.]+ \| malos detectados ([\d.]+)")
M["rf_cv_det"] = num(r"Random Forest\s+exactitud [\d.]+ ± [\d.]+ \| malos detectados ([\d.]+)")

registros = json.loads((RAIZ / "evidencia" / "textos_generados.json").read_text(encoding="utf-8"))
etiquetas = json.loads((RAIZ / "evidencia" / "etiquetas.json").read_text(encoding="utf-8"))
F200, F20 = medir(registros, etiquetas), medir(registros[:20], etiquetas)
assert len(F200) == 200


def resumen(filas):
    ant, des = Counter(), Counter()
    for f in filas:
        ant.update(motivos(f["antes"]))
        des.update(motivos(f["despues"]))
    return dict(
        ant=ant, des=des, rech_ant=sum(bool(f["antes"]) for f in filas), rech_des=sum(bool(f["despues"]) for f in filas),
        fp_ant=sum(bool(f["antes"]) and f["etiqueta"] == "correcto" for f in filas),
        fp_des=sum(bool(f["despues"]) and f["etiqueta"] == "correcto" for f in filas),
        inc_ant=sum(not f["antes"] and f["etiqueta"] == "incorrecto" for f in filas),
        inc_des=sum(not f["despues"] and f["etiqueta"] == "incorrecto" for f in filas),
        res_des=sum(not f["despues"] and f["etiqueta"] == "reserva" for f in filas),
        cor_des=sum(not f["despues"] and f["etiqueta"] == "correcto" for f in filas))


R200, R20 = resumen(F200), resumen(F20)
moneda = sum(1 for f in F200 if not f["despues"] and re.search(r"euros|\$|dólares", f["texto"].lower()))


def f3(x):                       # APA: sin cero inicial en valores acotados a 1
    return f"{x:.3f}".lstrip("0")


# ---------- documento ----------
doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Inches(8.5), Inches(11)
for lado in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
    setattr(sec, lado, Inches(1))
normal = doc.styles["Normal"]
normal.font.name, normal.font.size = FUENTE, Pt(11)
normal.element.rPr.rFonts.set(qn("w:eastAsia"), FUENTE)
normal.paragraph_format.line_spacing = INTERLINEADO
normal.paragraph_format.space_after = normal.paragraph_format.space_before = Pt(0)


def campo(par, instr):
    for tipo, txt in (("begin", None), (None, instr), ("end", None)):
        run = par.add_run()
        el = OxmlElement("w:fldChar" if tipo else "w:instrText")
        if tipo:
            el.set(qn("w:fldCharType"), tipo)
        else:
            el.set(qn("xml:space"), "preserve")
            el.text = txt
        run._r.append(el)


cab = sec.header.paragraphs[0]
cab.alignment = WD_ALIGN_PARAGRAPH.RIGHT
cab.paragraph_format.line_spacing = 1.0
campo(cab, "PAGE")


def parrafo(partes, indent=True, align=None, spacing=None, keep=False, sangria_francesa=False):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Inches(0.5)
    if sangria_francesa:
        p.paragraph_format.left_indent, p.paragraph_format.first_line_indent = Inches(0.5), Inches(-0.5)
    if align is not None:
        p.alignment = align
    if spacing:
        p.paragraph_format.line_spacing = spacing
    p.paragraph_format.keep_with_next = keep
    for t in (partes if isinstance(partes, list) else [partes]):
        texto, est = t if isinstance(t, tuple) else (t, "")
        r = p.add_run(texto)
        r.bold, r.italic = "b" in est, "i" in est
        if "c" in est:                                   # código
            r.font.name = "Consolas"
            r.font.size = Pt(9.5)
    return p


def titulo(texto):
    return parrafo([(texto, "b")], indent=False, align=WD_ALIGN_PARAGRAPH.CENTER, keep=True)


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


def tabla_apa(numero, titulo_tabla, encabezados, filas, anchos, nota, tam=9, negrita_ultimas=()):
    parrafo([(f"Tabla {numero}", "b")], indent=False, spacing=1.0, keep=True)
    parrafo([(titulo_tabla, "i")], indent=False, spacing=1.0, keep=True)
    t = doc.add_table(rows=1 + len(filas), cols=len(encabezados))
    t.autofit = False
    for i, enc in enumerate(encabezados):
        t.rows[0].cells[i].text = ""
        t.rows[0].cells[i].paragraphs[0].add_run(enc).bold = True
    for fila, datos in zip(t.rows[1:], filas):
        for i, txt in enumerate(datos):
            fila.cells[i].text = str(txt)
    for r_i, fila in enumerate(t.rows):
        for i, celda in enumerate(fila.cells):
            celda.width = anchos[i]
            for p in celda.paragraphs:
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.space_after = Pt(1.5)
                p.paragraph_format.keep_with_next = r_i < len(t.rows) - 1       # la tabla no se parte entre páginas
                if i > 0 and len(encabezados) > 3 and r_i >= 0 and len(str(celda.text)) < 14:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for r in p.runs:
                    r.font.size = Pt(tam)
                    if r_i - 1 in negrita_ultimas:
                        r.bold = True
    for celda in t.rows[0].cells:
        borde(celda, top=8, bottom=8)
    for celda in t.rows[-1].cells:
        borde(celda, bottom=8)
    parrafo([("Nota. ", "i"), nota], indent=False, spacing=1.0)
    parrafo("", indent=False, spacing=0.5)


C = WD_ALIGN_PARAGRAPH.CENTER
parrafo([("Aplicación híbrida con verificación: una red neuronal, un texto generado y dos reglas que cierran un hueco", "b")],
        indent=False, align=C, spacing=1.0)
for linea in (AUTOR, "Atlantis University · MAI 540: Machine Learning · Profesor: Kevin A. García Gallardo",
              "Tarea 7.2 · 19 de octubre de 2026"):
    parrafo(linea, indent=False, align=C, spacing=1.0)
parrafo("", indent=False, spacing=0.6)

parrafo(["La aplicación de la Clase 7 combina un Random Forest que estima la probabilidad de que un crédito sea malo, un modelo "
         "de lenguaje pequeño (Qwen2.5-0.5B-Instruct; Qwen Team, 2024) que redacta la explicación y un verificador que decide si "
         "el texto se muestra. Sobre las 200 solicitudes de prueba de German Credit (Hofmann, 1994; partición 80/20 estratificada, "
         "semilla 42) se comparó el predictor con una red neuronal, se buscó un fallo que el verificador de clase no atrapa, se "
         "cerró con dos reglas y se midió el efecto."])

# ---------- 1 ----------
titulo("Red neuronal y Random Forest")
parrafo([f"La red de ", ("crear_red", "c"), f" tiene 61 entradas (las categorías convertidas en columnas 0/1 más las variables "
         f"numéricas estandarizadas), dos capas ocultas de 16 y 8 neuronas con ReLU y una salida: {M['pesos']} pesos y sesgos "
         f"aprendidos. Sobre las 200 solicitudes que no vio acertó {f3(M['red_pru'])}; el Random Forest, {f3(M['rf_pru'])} "
         f"(Tabla 1). Con 200 casos el error típico de una exactitud ronda tres puntos, así que la diferencia de siete solicitudes "
         f"no es concluyente, aunque la validación cruzada apunta igual ({f3(M['red_cv'])} frente a {f3(M['rf_cv'])}). "
         f"Ambos quedan cerca de {f3(M['base'])}, la exactitud de responder siempre «bueno», y ambos memorizan el entrenamiento "
         f"({M['red_ent']:.2f}). La red aprende pesos continuos que combinan todas las variables en una sola superficie suave; "
         f"por eso detecta más créditos malos ({f3(M['red_det'])}) pero es sensible a la escala y al sobreajuste con solo 800 filas. "
         f"El bosque promedia 200 árboles de reglas del tipo «si la cuenta es negativa y el plazo es largo…» (Breiman, 2001), "
         f"admite categorías y números sin ajustes finos y es más estable (±{f3(M['rf_cv_sd'])} frente a ±{f3(M['red_cv_sd'])}). "
         f"Elegiría el Random Forest como predictor de esta aplicación; si aprobar un crédito malo costara mucho más que rechazar "
         f"uno bueno, ajustaría su umbral antes de pasarme a la red, que detecta {f3(M['red_det'])} de los malos contra "
         f"{f3(M['rf_det'])}."])

tabla_apa(1, "Red neuronal y Random Forest sobre las mismas 200 solicitudes de prueba",
          ["Modelo", "Estructura", "Exactitud entren.", "Exactitud prueba", "Malos detectados", "Exactitud val. cruzada"],
          [("Red neuronal (MLP)", f"61-16-8-1; {M['pesos']} pesos", f3(M['red_ent']), f3(M['red_pru']), f3(M['red_det']),
            f"{f3(M['red_cv'])} (±{f3(M['red_cv_sd'])})"),
           ("Random Forest", f"200 árboles; {M['nodos']} nodos", f3(M['rf_ent']), f3(M['rf_pru']), f3(M['rf_det']),
            f"{f3(M['rf_cv'])} (±{f3(M['rf_cv_sd'])})"),
           ("Siempre «bueno»", "—", "—", f3(M['base']), ".000", "—")],
          (Inches(1.3), Inches(1.5), Inches(0.9), Inches(0.9), Inches(0.9), Inches(1.0)),
          "«Malos detectados» es la proporción de los 60 créditos malos de la prueba que el modelo señaló. Validación cruzada de "
          "5 pliegues sobre los 1,000 casos (media y desviación estándar). Salida de comparar_modelos.py.")

# ---------- 2 ----------
n_tono = R200["ant"]["tono incoherente (<30% o >60%)"]
n_num = R200["ant"]["número no sustentado"]
n_abs = R200["ant"]["afirmación absoluta"]
titulo("Ejecución sobre 200 solicitudes y rechazos del verificador de clase")
parrafo([("main.py", "c"), f" recorre ahora N solicitudes (se ejecutó con 20 y con 200). El verificador de clase rechazó {R20['rech_ant']} "
         f"de las primeras 20 explicaciones y {R200['rech_ant']} de las 200 ({R200['rech_ant'] / 2:.0f} %). Los motivos fueron {n_tono} "
         f"llamadas «alto» con probabilidad menor de 30 % (o «bajo» con más de 60 %), {n_num} números que no vienen de los datos ni "
         f"del modelo y {n_abs} afirmación absoluta; un texto puede tener varios motivos. La Tabla 2 muestra dos casos reales: la "
         f"solicitud 1 llama «alto» a un 26 %, y la 18 afirma «más de 60 años» sobre una persona de 57."])

# ---------- 3 ----------
titulo("Un fallo que la verificación no atrapa")
parrafo([f"La solicitud 8 (43 %) pasó la verificación aunque su texto dice que la cuenta corriente está «sin saldo negativo» y el dato "
         f"es «saldo negativo». El verificador no lo ve porque solo mira números (43 %, 23 años y 6 meses son correctos) y el tono en "
         f"las franjas extremas, y 43 % queda en medio. No es un caso aislado: el mismo error aparece en {R200['des']['contradice un dato (cuenta/vivienda)']} "
         f"de los 200 textos, todos de solicitudes con saldo negativo, y la solicitud 4 añade «una persona sola», sin ningún dato "
         f"detrás. Apliqué a mano el protocolo del agente ", ("revisor-de-explicaciones", "c"), ", que agregué a la extensión porque "
         "la de la Tarea 7.1 solo tenía el auditor de equidad; no lo ejecuté dentro de Claude Code."])

tabla_apa(2, "Ejemplos reales (modelo Qwen2.5-0.5B-Instruct, generación determinista)",
          ["Solicitud", "Datos", "Texto del modelo de lenguaje (extracto)", "Resultado"],
          [("1 · 26 %", "36 años; 18 meses; saldo entre 0 y 200", "«…lo cual es alto para una persona con una edad de 36 años…»",
            "Rechazada (clase): «alto» con probabilidad baja."),
           ("18 · 14 %", "57 años; 11 meses; sin cuenta corriente", "«…ya que la edad es mayor a 60 años y la duración de la cuenta es muy corta…»",
            "Rechazada (clase): número no sustentado, 60."),
           ("8 · 43 %", "23 años; 6 meses; saldo negativo", "«…en una cuenta corriente sin saldo negativo.»",
            "Pasó la clase; rechazada por las reglas 1 y 2."),
           ("118 · 36 %", "47 años; 18 meses; sin cuenta corriente", "«…ya que la edad es alta (47 años) y la duración de la cuenta es corta…»",
            "Regla 2 inicial: falso motivo («riesgo alto»); tras el ajuste pasa.")],
          (Inches(0.8), Inches(1.35), Inches(2.6), Inches(1.75)),
          "Las probabilidades son las del predictor para la solicitud. Textos completos en evidencia/ejecucion_antes.txt.", tam=8.5)

# ---------- 4 ----------
titulo("Dos reglas nuevas")
parrafo([("Regla 1 (", ""), ("verificar_datos", "c"), "). Compara el texto con la cuenta corriente y la vivienda de la solicitud. Reconoce "
         "cuatro afirmaciones de cuenta (saldo negativo, entre 0 y 200, de 200 o más, sin cuenta) y tres de vivienda (propia, alquilada, "
         "sin costo) con expresiones regulares, ignora las precedidas por «no», «sin» o «ni», y rechaza las que dicen algo distinto "
         "del dato o que afirman atributos que los datos no contienen (estado civil, hijos, empleo, ingresos). ", ("Regla 2 (", ""),
         ("verificar_tono_medio", "c"), "). Con probabilidad de 30 % a 60 %, extremos incluidos como en el texto de respaldo, rechaza "
         "que el texto califique de alto o bajo al riesgo o a la probabilidad. Ambas se conectaron a ", ("verificar_explicacion", "c"),
         ", que suma ahora ", ("verificar_base", "c"), " (el verificador de clase, conservado para medir el «antes») y las dos reglas. "
         "Cada regla tiene su archivo de pruebas y su commit: 46 pruebas la primera y 20 la segunda. Contra el verificador de clase "
         "fallan 10 de las 46 y 14 de las 17 iniciales (las de rechazo por aserción; el resto, por no existir la función), y con las "
         "reglas pasan todas, igual que las cinco originales (71 de 71)."])

# ---------- 5 ----------
titulo("Efecto de las reglas y falsos positivos")


def fila(nombre):
    return (nombre, R20["ant"][nombre], R20["des"][nombre], R200["ant"][nombre], R200["des"][nombre])


tabla_apa(3, "Rechazos antes y después de las dos reglas, sobre los mismos textos",
          ["Motivo del rechazo", "20 antes", "20 después", "200 antes", "200 después"],
          [fila(n) for n, _ in MOTIVOS if n != "afirmación absoluta"] +
          [("Textos rechazados", R20["rech_ant"], R20["rech_des"], R200["rech_ant"], R200["rech_des"]),
           ("Falsos positivos (texto correcto rechazado)", R20["fp_ant"], R20["fp_des"], R200["fp_ant"], R200["fp_des"]),
           ("Textos incorrectos que se mostraron", R20["inc_ant"], R20["inc_des"], R200["inc_ant"], R200["inc_des"])],
          (Inches(2.9), Inches(0.9), Inches(0.9), Inches(0.9), Inches(0.9)),
          "Un texto con varios motivos cuenta en cada fila y una vez en «Textos rechazados»; la única afirmación absoluta (1 antes y 1 después) no se muestra. Incorrecto/correcto según "
          "lectura manual de cada texto contra sus datos (evidencia/etiquetas.json; un solo revisor). Salida de medir_efecto.py.",
          negrita_ultimas=(len(MOTIVOS) - 1,))

parrafo([f"Los rechazos pasaron de {R200['rech_ant']} a {R200['rech_des']} de 200 y los textos incorrectos que se mostraban, de "
         f"{R200['inc_ant']} a {R200['inc_des']}; los {R200['cor_des']} textos correctos siguieron mostrándose, es decir, ningún "
         f"rechazo final fue un falso positivo. Sí hubo una regla que se disparó por un motivo falso: en las solicitudes 118 y 158 la "
         f"Regla 2 leyó «la edad es alta (47 años)» como un juicio sobre el riesgo. El texto era incorrecto por otra causa (llama "
         f"«duración de la cuenta» a la del crédito), pero con una frase correcta habría sido un falso positivo. Lo ajusté: "
         f"«es alto/a» se ignora si lo precede edad, monto, duración, saldo o cuenta, salvo «lo cual», «lo que» o «esto», que sí "
         f"se refieren al riesgo; dos pruebas nuevas fallaban antes del ajuste. El costo es que esos dos textos ahora pasan. También "
         f"cambiaría el rechazo por revisión humana cuando haya una duda explícita («podría indicar un riesgo alto», solicitud 182)."])

# ---------- 6 ----------
titulo("Límites y recomendación")
parrafo([f"Tras las reglas, {R200['inc_des']} de 200 textos incorrectos (11 %) siguen pasando y {R200['res_des']} más hacen "
         f"afirmaciones evaluativas sin respaldo. Son cuatro patrones: el sentido de la probabilidad invertido (4; «hay una menor "
         f"probabilidad de que el cliente pueda pagar» con 30 % de crédito malo), una cifra o un campo atribuido al lugar equivocado "
         f"(14; «el monto total de la cuenta corriente es de $2058» para quien no tiene cuenta), frases incoherentes (3) y calificativos "
         f"falsos (1; duración «muy corta» con 45 meses). Además, {moneda} de los {R200['cor_des'] + R200['inc_des'] + R200['res_des']} "
         f"textos que pasan hablan de «euros» o «$» y los datos no traen moneda. Un verificador de reglas no puede cerrar esto del "
         f"todo: cada regla enumera una forma de decir algo y el lenguaje tiene infinitas paráfrasis; saber si una cifra pertenece al "
         f"campo mencionado, si un adjetivo describe lo correcto o si una inferencia conserva el sentido exige interpretar la oración, "
         f"y las reglas solo cubren lo ya observado (los modelos de lenguaje producen afirmaciones fluidas pero no respaldadas; Ji et "
         f"al., 2023). Además, las etiquetas son de un solo revisor y de un solo modelo pequeño."])
parrafo(["Para un banco recomendaría: (a) no mostrar al cliente el texto libre del modelo de lenguaje, sino la explicación de "
         "respaldo armada con datos, y usar el modelo solo para borradores internos; (b) revisión humana obligatoria antes de "
         "cualquier texto que acompañe una negativa y siempre que la probabilidad esté entre 30 % y 60 % o falle una regla; (c) "
         "razones tomadas de las variables que de verdad pesaron en el predictor, registro de cada texto mostrado y auditoría "
         "periódica por muestreo con etiquetas humanas, incluida la equidad por grupo de la Tarea 7.1; y (d) tratarlo como sistema "
         "de alto riesgo, pues evaluar la solvencia de personas lo es en el Reglamento (UE) 2024/1689 y exige supervisión humana."])

titulo("Referencias")
refs = [
    ["Breiman, L. (2001). Random forests. ", ("Machine Learning, 45", "i"), "(1), 5–32. https://doi.org/10.1023/A:1010933404324"],
    ["Hofmann, H. (1994). ", ("Statlog (German Credit Data)", "i"), " [Conjunto de datos]. UCI Machine Learning Repository. "
     "https://doi.org/10.24432/C5NC77"],
    ["Ji, Z., Lee, N., Frieske, R., Yu, T., Su, D., Xu, Y., Ishii, E., Bang, Y., Madotto, A., y Fung, P. (2023). Survey of "
     "hallucination in natural language generation. ", ("ACM Computing Surveys, 55", "i"), "(12), Artículo 248. https://doi.org/10.1145/3571730"],
    ["Qwen Team. (2024). ", ("Qwen2.5 technical report", "i"), ". arXiv. https://arxiv.org/abs/2412.15115"],
    ["Unión Europea. (2024). Reglamento (UE) 2024/1689 por el que se establecen normas armonizadas en materia de inteligencia "
     "artificial. ", ("Diario Oficial de la Unión Europea", "i"), ". https://eur-lex.europa.eu/eli/reg/2024/1689/oj"],
]
for r in refs:
    parrafo(r, sangria_francesa=True, indent=False, spacing=1.0)

salida_docx = RAIZ / "informe" / "Informe_Tarea_7_2.docx"
doc.save(salida_docx)
print("Informe generado:", salida_docx)
