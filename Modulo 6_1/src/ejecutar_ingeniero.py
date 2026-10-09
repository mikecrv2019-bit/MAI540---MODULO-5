"""Rol 2: ejecuta CV y particion unica para ambos modelos y escribe la evidencia.

Salidas: evidencia/02_ingeniero_modelos/metricas.json y metricas.md
Determinista: sin fechas ni tiempos. Desviacion estandar muestral (ddof=1).
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from datos import cargar_datos  # noqa: E402
from modelos import crear_pipeline, dos_modelos  # noqa: E402
from particion_unica import SEMILLAS, TEST_SIZE, evaluar_semillas  # noqa: E402
from validacion import N_PLIEGUES, SEMILLA_CV, resumen, validar_cv  # noqa: E402

SALIDA = RAIZ / "evidencia" / "02_ingeniero_modelos"
LINEA_BASE = 0.70
NOMBRES = {"arbol": "Arbol de decision", "random_forest": "Random Forest"}


def diferencias(res_part, media_cv):
    """Media de particiones - media CV, y min/max frente a la media CV (en pp)."""
    return {
        "media_menos_media_cv_pp": (res_part["media"] - media_cv) * 100,
        "min_menos_media_cv_pp": (res_part["min"] - media_cv) * 100,
        "max_menos_media_cv_pp": (res_part["max"] - media_cv) * 100,
    }


def main():
    X, y, cols_cat = cargar_datos()
    cols_num = [c for c in X.columns if c not in cols_cat]
    out = {
        "config": {
            "n_filas": int(len(X)), "n_cols_cat": len(cols_cat), "n_cols_num": len(cols_num),
            "cols_cat": cols_cat, "cols_num": cols_num,
            "cv": f"StratifiedKFold(n_splits={N_PLIEGUES}, shuffle=True, random_state={SEMILLA_CV})",
            "particion": f"train_test_split(test_size={TEST_SIZE}, stratify=y, random_state=s)",
            "semillas_particion": SEMILLAS, "semillas_subconjunto": list(range(10)),
            "modelos": "DecisionTreeClassifier(random_state=42); RandomForestClassifier(random_state=42); resto por defecto",
            "preprocesamiento": "ColumnTransformer: OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1) en categoricas; numericas 'passthrough'",
            "desviacion": "desviacion estandar muestral (ddof=1)",
            "clase_positiva": "bad (y=1)",
        },
        "linea_base_siempre_bueno": LINEA_BASE,
        "linea_base_calculada": float((y == 0).mean()),
        "modelos": {},
    }
    for clave, est in dos_modelos().items():
        pipe = crear_pipeline(est, cols_cat, cols_num)
        cv = validar_cv(pipe, X, y)
        cv_acc = resumen(cv["exactitud_por_pliegue"])
        cv_rec = resumen(cv["recall_bad_por_pliegue"])
        por_semilla = evaluar_semillas(pipe, X, y, SEMILLAS)
        bloque = {"cv": {**cv, "exactitud": cv_acc, "recall_bad": cv_rec},
                  "particion_unica": {"por_semilla": por_semilla}}
        for etiqueta, semillas in (("semillas_0_29", SEMILLAS), ("semillas_0_9", list(range(10)))):
            acc = resumen([por_semilla[s]["exactitud"] for s in semillas])
            rec = resumen([por_semilla[s]["recall_bad"] for s in semillas])
            bloque["particion_unica"][etiqueta] = {
                "exactitud": acc, "recall_bad": rec,
                "dif_exactitud_vs_cv": diferencias(acc, cv_acc["media"]),
                "dif_recall_bad_vs_cv": diferencias(rec, cv_rec["media"]),
            }
        out["modelos"][clave] = bloque

    SALIDA.mkdir(parents=True, exist_ok=True)
    (SALIDA / "metricas.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    (SALIDA / "metricas.md").write_text(redactar_md(out), encoding="utf-8")
    print("OK: evidencia escrita en", SALIDA.relative_to(RAIZ))


def f(v):
    return f"{v:.4f}"


def pp(v):
    return f"{v:+.2f}"


def redactar_md(o):
    L = []
    c = o["config"]
    L += ["# Metricas del ingeniero de modelos", "",
          "Generado por `src/ejecutar_ingeniero.py` (todas las cifras provienen de ese calculo; determinista).", "",
          f"- Datos: {c['n_filas']} filas, {c['n_cols_cat']} categoricas y {c['n_cols_num']} numericas. Clase positiva: {c['clase_positiva']}.",
          f"- Linea base «siempre bueno»: exactitud = {o['linea_base_siempre_bueno']:.2f} (calculada: {f(o['linea_base_calculada'])}).",
          f"- Validacion cruzada: `{c['cv']}`.",
          f"- Particion unica: `{c['particion']}`, semillas 0 a 29 (y subconjunto 0 a 9).",
          f"- Modelos: {c['modelos']}.",
          f"- Preprocesamiento (dentro del Pipeline): {c['preprocesamiento']}.",
          f"- Dispersion: {c['desviacion']}.", ""]

    L += ["## 1. Validacion cruzada (5 pliegues)", "",
          "| Modelo | Exactitud media | Exactitud desv. | Recall bad media | Recall bad desv. | Recall bad agregado (cross_val_predict, dato adicional) |",
          "|---|---|---|---|---|---|"]
    for k, m in o["modelos"].items():
        cv = m["cv"]
        L.append(f"| {NOMBRES[k]} | {f(cv['exactitud']['media'])} | {f(cv['exactitud']['desv'])} | "
                 f"{f(cv['recall_bad']['media'])} | {f(cv['recall_bad']['desv'])} | {f(cv['recall_bad_agregado_cross_val_predict'])} |")
    L += ["", "Valores por pliegue:", "",
          "| Modelo | Metrica | P1 | P2 | P3 | P4 | P5 |", "|---|---|---|---|---|---|---|"]
    for k, m in o["modelos"].items():
        L.append(f"| {NOMBRES[k]} | Exactitud | " + " | ".join(f(v) for v in m["cv"]["exactitud_por_pliegue"]) + " |")
        L.append(f"| {NOMBRES[k]} | Recall bad | " + " | ".join(f(v) for v in m["cv"]["recall_bad_por_pliegue"]) + " |")

    for etiqueta, titulo in (("semillas_0_29", "2. Particion unica 75/25, semillas 0 a 29"),
                             ("semillas_0_9", "3. Particion unica 75/25, solo semillas 0 a 9")):
        L += ["", f"## {titulo}", "",
              "| Modelo | Metrica | Min | Max | Media | Desv. | Media - media CV (pp) | Min - media CV (pp) | Max - media CV (pp) |",
              "|---|---|---|---|---|---|---|---|---|"]
        for k, m in o["modelos"].items():
            b = m["particion_unica"][etiqueta]
            for met, nom, dk in (("exactitud", "Exactitud", "dif_exactitud_vs_cv"),
                                 ("recall_bad", "Recall bad", "dif_recall_bad_vs_cv")):
                r, d = b[met], b[dk]
                L.append(f"| {NOMBRES[k]} | {nom} | {f(r['min'])} | {f(r['max'])} | {f(r['media'])} | {f(r['desv'])} | "
                         f"{pp(d['media_menos_media_cv_pp'])} | {pp(d['min_menos_media_cv_pp'])} | {pp(d['max_menos_media_cv_pp'])} |")
    L += ["", "Rango de la particion unica frente a la media CV: [min - media CV, max - media CV] en puntos porcentuales (pp), columnas finales de las tablas.", ""]

    L += ["## 4. Comparacion con la linea base", ""]
    for k, m in o["modelos"].items():
        L.append(f"- {NOMBRES[k]}: exactitud media CV = {f(m['cv']['exactitud']['media'])} frente a la linea base {o['linea_base_siempre_bueno']:.2f} "
                 f"(diferencia {pp((m['cv']['exactitud']['media'] - o['linea_base_siempre_bueno']) * 100)} pp).")

    L += ["", "## 5. Decisiones tomadas", "",
          "1. Parametros por defecto de scikit-learn salvo `random_state=42`; no hubo busqueda de hiperparametros.",
          "2. Unico preprocesamiento: `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)` en las 13 categoricas y `passthrough` en las 7 numericas, dentro del Pipeline (se ajusta en cada pliegue/particion de entrenamiento).",
          "3. Por indicacion del orquestador no se aplico escalado, logaritmos ni tratamiento de las numericas discretas como categoricas (propuestas del analista, no aplicadas).",
          "4. Recall de bad en CV calculado por pliegue (`scoring='recall'`, positivo = 1); el recall agregado de `cross_val_predict` se reporta solo como dato adicional.",
          "5. Desviacion estandar muestral (ddof=1) en todas las tablas; la CV usa 5 valores y las particiones 30 (o 10) valores.",
          "6. La CV y el `cross_val_predict` usan el mismo objeto `StratifiedKFold` con semilla 42, por lo que generan los mismos pliegues.",
          "7. La semilla del modelo (42) es fija en todas las particiones; solo cambia la semilla de la particion (0..29).",
          "8. `src/datos.py` y `datos/credit_g.csv` no se modificaron.", ""]

    mod = o["modelos"]
    L += ["## 6. Qué debe verificar el auditor", "",
          "Afirmaciones concretas de este entregable:", "",
          "1. Los dos modelos son `DecisionTreeClassifier(random_state=42)` y `RandomForestClassifier(random_state=42)` con el resto por defecto.",
          "2. La CV es `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` y el preprocesamiento esta dentro del Pipeline (sin fuga: no se transforma nada fuera de el).",
          "3. Las particiones usan `train_test_split(test_size=0.25, stratify=y, random_state=s)` con s = 0..29.",
          "4. El recall de bad por pliegue usa la clase y=1 como positiva; la media/desv. son de los 5 recalls por pliegue.",
          "5. Cifras a reproducir: " + "; ".join(
              f"{NOMBRES[k]} exactitud CV {f(mod[k]['cv']['exactitud']['media'])} +/- {f(mod[k]['cv']['exactitud']['desv'])}, "
              f"recall bad CV {f(mod[k]['cv']['recall_bad']['media'])} +/- {f(mod[k]['cv']['recall_bad']['desv'])}" for k in mod) + ".",
          "6. Las diferencias en pp se calculan restando la media CV a la media/min/max de las particiones unicas (columnas de las secciones 2 y 3).",
          "7. La ejecucion es determinista: volver a correr `python src/ejecutar_ingeniero.py` debe regenerar `metricas.json` y `metricas.md` identicos.",
          "8. El script no modifica `src/datos.py` ni `datos/credit_g.csv`.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    main()
