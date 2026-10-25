"""Logica de la demostracion (sin Gradio, para poder probarla): clasifica un lote o un archivo CSV y avisa de deriva.

La interfaz web esta en app_gradio.py y solo llama a estas funciones.
"""
import pandas as pd

from datos import OBJETIVO, PREDICTORAS, RUTA_DATOS, cargar_datos
from deriva import mensaje_deriva, reporte_deriva
from entrenar import RUTA_MODELO, ejecutar
from predecir import cargar_modelo, clasificar_lote

UMBRAL_CONFIANZA = 0.80   # en detalle_errores.py los 3 errores de 178 lotes tuvieron confianza < 0.68, y 12 lotes < 0.80
MIN_LOTES_ARCHIVO = 1
MAX_LOTES_ARCHIVO = 5000

# Nombre que ve la persona -> nombre de la columna. El orden es el de PREDICTORAS.
ETIQUETAS = {
    "alcohol": "Alcohol", "malic_acid": "Ácido málico", "ash": "Ceniza",
    "alcalinity_of_ash": "Alcalinidad de la ceniza", "magnesium": "Magnesio", "total_phenols": "Fenoles totales",
    "flavanoids": "Flavonoides", "nonflavanoid_phenols": "Fenoles no flavonoides", "proanthocyanins": "Proantocianinas",
    "color_intensity": "Intensidad de color", "hue": "Tono", "od280/od315_of_diluted_wines": "OD280/OD315 (vino diluido)",
    "proline": "Prolina",
}
# Lotes del archivo de datos para probar la demostracion: uno por perfil y uno ambiguo (el 83 falla en las 3 repeticiones).
EJEMPLOS = {"Lote típico class_0": 0, "Lote típico class_1": 100, "Lote típico class_2": 150, "Lote ambiguo (el 83)": 83}


def asegurar_modelo():
    """Un clon limpio no trae el modelo (modelos/ no se versiona): se entrena una vez, tarda unos segundos."""
    if not RUTA_MODELO.exists():
        print("No hay modelo guardado: entrenando (unos segundos)...")
        ejecutar()


def valores_de_ejemplo(nombre):
    """Las 13 mediciones del lote de ejemplo, en el orden de PREDICTORAS."""
    X, _ = cargar_datos(RUTA_DATOS)
    return [round(float(X.iloc[EJEMPLOS[nombre]][c]), 4) for c in PREDICTORAS]


def valores_tipicos():
    """Mediana de cada variable: el valor con que arranca el formulario."""
    X, _ = cargar_datos(RUTA_DATOS)
    return [round(float(X[c].median()), 4) for c in PREDICTORAS]


def evaluar_lote(valores):
    """`valores`: las 13 mediciones en el orden de PREDICTORAS. Devuelve (probabilidades, texto para la persona)."""
    asegurar_modelo()
    try:
        r = clasificar_lote(dict(zip(PREDICTORAS, valores)))
    except ValueError as e:
        return {}, f"**No se pudo clasificar:** {e}"
    confianza = max(r["probabilidades"].values())
    texto = [f"**Perfil químico más parecido: {r['perfil']}** (confianza {confianza:.0%}). "
             "Es una descripción del lote, no la línea de producto."]
    if confianza < UMBRAL_CONFIANZA:
        texto.append(f"**Confianza baja (< {UMBRAL_CONFIANZA:.0%}).** En la validación, los errores se concentraron aquí: "
                     "revise el lote con el enólogo antes de usar este resultado.")
    for a in r["advertencias"]:
        texto.append(f"**Fuera de rango:** {a}. El modelo extrapola; desconfíe del resultado.")
    return r["probabilidades"], "\n\n".join(texto)


def leer_archivo(ruta):
    """Lee un CSV con las 13 variables (y opcionalmente `cultivar`). Falla con un mensaje claro si no cumple."""
    try:
        df = pd.read_csv(ruta)
    except Exception as e:  # archivo vacio, no es CSV, codificacion rara...
        raise ValueError(f"No pude leer el archivo como CSV: {e}") from e
    faltan = [c for c in PREDICTORAS if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas: {faltan}. El archivo debe tener las 13 variables del archivo de ejemplo.")
    if not MIN_LOTES_ARCHIVO <= len(df) <= MAX_LOTES_ARCHIVO:
        raise ValueError(f"El archivo debe tener entre {MIN_LOTES_ARCHIVO} y {MAX_LOTES_ARCHIVO} lotes; tiene {len(df)}.")
    num = df[PREDICTORAS].apply(pd.to_numeric, errors="coerce")
    malas = num.isna().any(axis=1)
    if malas.any():
        filas = (malas[malas].index[:5] + 2).tolist()   # +2: encabezado y fila 1 de Excel
        raise ValueError(f"Hay valores vacíos o que no son números (filas {filas} del archivo, entre otras).")
    df[PREDICTORAS] = num
    return df


def evaluar_archivo(ruta):
    """Clasifica todos los lotes del archivo y los compara con los datos de entrenamiento. Devuelve (tabla, resumen)."""
    asegurar_modelo()
    try:
        df = leer_archivo(ruta)
    except ValueError as e:
        return pd.DataFrame(), f"**No se pudo procesar el archivo:** {e}"
    modelo = cargar_modelo()["modelo"]   # una sola lectura del modelo para todo el archivo
    prob = modelo.predict_proba(df[PREDICTORAS])
    tabla = df.reset_index(drop=True)
    tabla["perfil"] = modelo.classes_[prob.argmax(axis=1)]
    tabla["confianza"] = prob.max(axis=1).round(3)
    tabla["revisar"] = tabla["confianza"] < UMBRAL_CONFIANZA
    X_ref, _ = cargar_datos(RUTA_DATOS)
    texto = [f"**{len(tabla)} lotes clasificados.** {int(tabla['revisar'].sum())} con confianza baja (revisar).",
             "**Deriva:** " + mensaje_deriva(reporte_deriva(X_ref, tabla[PREDICTORAS]))]
    if OBJETIVO in df.columns:
        reales = df[OBJETIVO].astype(str).to_numpy()
        texto.append(f"**Con las etiquetas que trae el archivo:** exactitud {(tabla['perfil'].to_numpy() == reales).mean():.1%} "
                     "(este es el control que sí detecta la degradación; la validación fue 0.981 ± 0.022).")
    return tabla, "\n\n".join(texto)
