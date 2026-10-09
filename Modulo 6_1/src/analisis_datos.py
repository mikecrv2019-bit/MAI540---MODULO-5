"""Analisis descriptivo de German Credit (Rol 1: Analista de datos).

Genera evidencia/01_analista_datos/resumen_datos.md y resumen_datos.json.
No entrena modelos, no particiona, no transforma los datos. Salida determinista.
"""
import json
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from datos import cargar_datos  # noqa: E402

RUTA_CSV = RAIZ / "datos" / "credit_g.csv"
DIR_SALIDA = RAIZ / "evidencia" / "01_analista_datos"
UMBRAL_CATEGORIA_RARA = 10  # nº de filas


def r(x, n=4):
    return round(float(x), n)


def analizar():
    X, y, cols_cat = cargar_datos(RUTA_CSV)
    cols_num = [c for c in X.columns if c not in cols_cat]
    n = len(X)
    n_bad = int(y.sum())
    n_good = n - n_bad

    res = {
        "archivo": "datos/credit_g.csv",
        "forma_X": [int(X.shape[0]), int(X.shape[1])],
        "n_columnas_categoricas": len(cols_cat),
        "columnas_categoricas": cols_cat,
        "n_columnas_numericas": len(cols_num),
        "columnas_numericas": cols_num,
        "clase": {
            "good_0": n_good,
            "bad_1": n_bad,
            "proporcion_good": r(n_good / n),
            "proporcion_bad": r(n_bad / n),
            "linea_base_siempre_bueno_exactitud": r(n_good / n),
        },
    }

    # Faltantes
    falt = X.isna().sum()
    res["valores_faltantes"] = {
        "total_en_X": int(falt.sum()),
        "total_en_y": int(y.isna().sum()),
        "columnas_con_faltantes": {c: int(v) for c, v in falt.items() if v > 0},
    }

    # Duplicados
    df_completo = X.assign(clase=y)
    res["duplicados"] = {
        "filas_duplicadas_X": int(X.duplicated().sum()),
        "filas_duplicadas_X_y_clase": int(df_completo.duplicated().sum()),
        "filas_X_identicas_con_clase_distinta": int(
            (df_completo.drop_duplicates().duplicated(subset=list(X.columns), keep=False)).sum()
        ),
    }

    # Categoricas
    cat = {}
    for c in cols_cat:
        vc = X[c].value_counts()
        tasa_bad = y.groupby(X[c]).mean()
        cat[c] = {
            "cardinalidad": int(X[c].nunique()),
            "categorias": {k: int(v) for k, v in vc.items()},
            "tasa_bad_por_categoria": {k: r(tasa_bad[k]) for k in vc.index},
        }
    res["categoricas"] = cat

    # Numericas
    num = {}
    for c in cols_num:
        s = X[c]
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        fuera = int(((s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)).sum())
        num[c] = {
            "min": r(s.min()), "max": r(s.max()), "media": r(s.mean()),
            "mediana": r(s.median()), "desv_est": r(s.std()),
            "q1": r(q1), "q3": r(q3), "asimetria": r(s.skew()),
            "valores_unicos": int(s.nunique()),
            "atipicos_iqr_1_5": fuera,
            "ceros": int((s == 0).sum()),
            "negativos": int((s < 0).sum()),
        }
    res["numericas"] = num

    # Anomalias / observaciones (todas derivadas de calculos)
    anom = []
    for c in cols_cat:
        raras = {k: v for k, v in cat[c]["categorias"].items() if v <= UMBRAL_CATEGORIA_RARA}
        if raras:
            anom.append(f"'{c}' tiene categorias con <= {UMBRAL_CATEGORIA_RARA} filas: {raras}.")
        if X[c].str.strip().ne(X[c]).any():
            anom.append(f"'{c}' tiene valores con espacios al inicio o al final.")
    pocas = [c for c in cols_num if num[c]["valores_unicos"] <= 5]
    if pocas:
        anom.append(
            "Columnas numericas con <= 5 valores distintos (discretas/ordinales, "
            f"tratables como categoricas): {pocas}."
        )
    for c in cols_num:
        if abs(num[c]["asimetria"]) > 1:
            anom.append(
                f"'{c}' es asimetrica (asimetria={num[c]['asimetria']}, max={num[c]['max']}, "
                f"mediana={num[c]['mediana']}, {num[c]['atipicos_iqr_1_5']} atipicos IQR)."
            )
    if res["clase"]["proporcion_bad"] < 0.4:
        anom.append(
            f"Clase desbalanceada: bad={n_bad} ({res['clase']['proporcion_bad']:.1%}) frente a "
            f"good={n_good}; una exactitud <= {res['clase']['linea_base_siempre_bueno_exactitud']:.1%} "
            "no supera la linea base trivial."
        )
    if res["duplicados"]["filas_duplicadas_X"] == 0 and res["valores_faltantes"]["total_en_X"] == 0:
        anom.append("No se hallaron duplicados ni faltantes: no se propone limpiar filas.")
    # Etiquetas literales que pandas podria leer como NaN
    lit = {c: int(X[c].isin(["none", "None", "NA", "N/A", "null"]).sum()) for c in cols_cat}
    lit = {c: v for c, v in lit.items() if v}
    if lit:
        anom.append(
            f"Hay categorias con texto literal 'none' (valor valido, no faltante): {lit}. "
            "cargar_datos() las conserva como texto."
        )
    res["anomalias"] = anom

    res["instrucciones_para_ingeniero"] = [
        "Usar siempre cargar_datos() de src/datos.py; X llega sin transformar.",
        "Codificar las categoricas (cols_cat) y escalar las numericas SOLO dentro de un Pipeline "
        "(p. ej. ColumnTransformer), de modo que el ajuste ocurra unicamente con los datos de "
        "entrenamiento de cada particion.",
        "Definir las particiones (validacion cruzada y/o train/test) en su propio modulo, "
        "estratificadas por y, con semillas fijas.",
        f"Comparar toda exactitud contra la linea base «siempre bueno» "
        f"({res['clase']['linea_base_siempre_bueno_exactitud']:.1%}); reportar tambien metricas "
        "sensibles a la clase minoritaria (recall/F1/AUC de 'bad').",
        "No modificar datos/credit_g.csv. Cualquier limpieza propuesta debe reportarse; aqui no "
        "se propone ninguna fila a eliminar.",
        "Propuesta (no aplicada): considerar tratar como categoricas las numericas discretas "
        "listadas en las anomalias y/o transformar logaritmicamente credit_amount y duration "
        "dentro del Pipeline, a criterio del ingeniero.",
    ]
    return res


def a_markdown(res):
    L = []
    a = L.append
    f = res["forma_X"]
    cl = res["clase"]
    a("# Resumen de datos · German Credit\n")
    a(f"Archivo: `{res['archivo']}`. Generado por `src/analisis_datos.py` (todas las cifras provienen de ese cálculo).\n")
    a("## Forma y tipos\n")
    a(f"- Forma de `X`: **{f[0]} filas x {f[1]} columnas**.")
    a(f"- Categóricas ({res['n_columnas_categoricas']}): {', '.join(res['columnas_categoricas'])}.")
    a(f"- Numéricas ({res['n_columnas_numericas']}): {', '.join(res['columnas_numericas'])}.\n")
    a("## Variable objetivo (`clase`; 1 = bad, 0 = good)\n")
    a("| Clase | Filas | Proporción |\n|---|---|---|")
    a(f"| good (0) | {cl['good_0']} | {cl['proporcion_good']:.1%} |")
    a(f"| bad (1) | {cl['bad_1']} | {cl['proporcion_bad']:.1%} |\n")
    a(f"**Línea base «siempre bueno»: exactitud = {cl['linea_base_siempre_bueno_exactitud']:.4f}** "
      f"({cl['linea_base_siempre_bueno_exactitud']:.1%}).\n")
    a("## Calidad\n")
    fa, du = res["valores_faltantes"], res["duplicados"]
    a(f"- Valores faltantes en `X`: {fa['total_en_X']}; en `y`: {fa['total_en_y']}.")
    a(f"- Filas duplicadas en `X`: {du['filas_duplicadas_X']}; duplicadas incluyendo la clase: "
      f"{du['filas_duplicadas_X_y_clase']}; filas con `X` idéntico y clase distinta: "
      f"{du['filas_X_identicas_con_clase_distinta']}.\n")
    a("## Variables categóricas (cardinalidad y tasa de `bad`)\n")
    a("| Columna | Cardinalidad | Categorías (n; tasa bad) |\n|---|---|---|")
    for c, d in res["categoricas"].items():
        cats = "; ".join(f"{k} ({v}; {d['tasa_bad_por_categoria'][k]:.2f})" for k, v in d["categorias"].items())
        a(f"| {c} | {d['cardinalidad']} | {cats} |")
    a("\n## Variables numéricas (rangos)\n")
    a("| Columna | Mín | Máx | Media | Mediana | Desv. est. | Únicos | Asimetría | Atípicos IQR |\n|---|---|---|---|---|---|---|---|---|")
    for c, d in res["numericas"].items():
        a(f"| {c} | {d['min']:g} | {d['max']:g} | {d['media']:.2f} | {d['mediana']:g} | "
          f"{d['desv_est']:.2f} | {d['valores_unicos']} | {d['asimetria']:.2f} | {d['atipicos_iqr_1_5']} |")
    a("\n## Anomalías y observaciones\n")
    for t in res["anomalias"]:
        a(f"- {t}")
    a("\n## Instrucciones para el ingeniero de modelos\n")
    for i, t in enumerate(res["instrucciones_para_ingeniero"], 1):
        a(f"{i}. {t}")
    a("")
    return "\n".join(L)


def main():
    res = analizar()
    DIR_SALIDA.mkdir(parents=True, exist_ok=True)
    with open(DIR_SALIDA / "resumen_datos.json", "w", encoding="utf-8", newline="\n") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2, sort_keys=False)
        fh.write("\n")
    with open(DIR_SALIDA / "resumen_datos.md", "w", encoding="utf-8", newline="\n") as fh:
        fh.write(a_markdown(res))
    print("Resumen escrito en", DIR_SALIDA.relative_to(RAIZ).as_posix())


if __name__ == "__main__":
    main()
