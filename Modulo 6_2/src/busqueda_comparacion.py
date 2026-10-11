"""Etapa 1 · Busqueda de hiperparametros, medicion honesta y comparacion de tres modelos.

Uso:  python src/busqueda_comparacion.py
Escribe evidencia/busqueda_comparacion.json y .md. Todas las cifras del informe salen de ese JSON.
Determinista salvo los tiempos de ajuste (dependen del equipo y de la carga).
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.base import clone

sys.path.insert(0, str(Path(__file__).resolve().parent))
from busqueda import PARAM_GRID, buscar, parametros_limpios, validacion_anidada
from datos import RAIZ, VARIABLES_SENSIBLES, cargar_datos, predictoras
from modelos import NOMBRES, crear_pipeline, estimadores_base
from validacion import (SEMILLA_CV, SEMILLA_CV_INTERNA, crear_cv, evaluar, linea_base_siempre_bueno,
                        matriz_y_metricas, resumen)

SALIDA = RAIZ / "evidencia"
# Cifras de la Tarea 6.1 (evidencia/02_ingeniero_modelos/metricas.md de ese repo), con las 20 variables.
CIFRAS_6_1 = {"arbol_defecto": 0.6980, "random_forest": 0.7590}


def empaquetar(res, y):
    """Resume una evaluacion (por pliegue -> media/desv, tiempos y matriz de confusion agregada)."""
    return {
        "exactitud": resumen(res["exactitud_por_pliegue"]),
        "recall_bad": resumen(res["recall_bad_por_pliegue"]),
        "tiempo_ajuste_s": resumen(res["tiempo_ajuste_por_pliegue_s"]),
        "exactitud_por_pliegue": res["exactitud_por_pliegue"],
        "recall_bad_por_pliegue": res["recall_bad_por_pliegue"],
        "tiempo_ajuste_por_pliegue_s": res["tiempo_ajuste_por_pliegue_s"],
        "matriz_fuera_de_pliegue": matriz_y_metricas(y, res["prediccion_fuera_de_pliegue"]),
    }


def main():
    X_todas, y = cargar_datos()
    X = predictoras(X_todas)                      # sin variables sensibles: lo que el modelo usa para decidir
    cv = crear_cv()
    base = linea_base_siempre_bueno(y)
    n_bad, n_good = int(y.sum()), int((1 - y).sum())
    out = {"datos": {"filas": len(y), "bad": n_bad, "good": n_good, "razon_desbalance": n_good / n_bad,
                     "linea_base_siempre_bueno": base, "predictoras": list(X.columns),
                     "excluidas_por_sensibles": VARIABLES_SENSIBLES},
           "protocolo": {"cv_externa": f"StratifiedKFold(n_splits=5, shuffle=True, random_state={SEMILLA_CV})",
                         "cv_interna_busqueda": f"StratifiedKFold(n_splits=5, shuffle=True, random_state={SEMILLA_CV_INTERNA})",
                         "param_grid": {k: [("None" if v is None else v) for v in vs] for k, vs in PARAM_GRID.items()},
                         "combinaciones": int(np.prod([len(v) for v in PARAM_GRID.values()]))}}

    print(f"Datos: {len(y)} filas | bad={n_bad} good={n_good} | razon good/bad={n_good / n_bad:.2f} "
          f"| linea base 'siempre bueno' = {base:.4f}")
    print(f"Predictoras ({X.shape[1]}): sensibles excluidas = {VARIABLES_SENSIBLES}")

    # ---- 0. Control: reproducir las cifras de la Tarea 6.1 (20 variables, parametros por defecto) ----
    print("\n== 0. Control: reproducir la Tarea 6.1 (20 variables) ==")
    control = {}
    for clave in ("arbol_defecto", "random_forest"):
        est = estimadores_base()[clave]
        r = evaluar(crear_pipeline(est, X_todas), X_todas, y, cv)
        m = float(np.mean(r["exactitud_por_pliegue"]))
        control[clave] = {"exactitud_media": m, "cifra_tarea_6_1": CIFRAS_6_1[clave],
                          "coincide": bool(abs(m - CIFRAS_6_1[clave]) < 5e-4)}
        print(f"{NOMBRES[clave]:22s} exactitud CV = {m:.4f} | Tarea 6.1 = {CIFRAS_6_1[clave]:.4f} "
              f"| coincide: {control[clave]['coincide']}")
    out["control_tarea_6_1"] = control

    # ---- 1. Busqueda sistematica (GridSearchCV) sobre las 18 predictoras ----
    print("\n== 1. Busqueda sistematica con GridSearchCV (arbol) ==")
    pipe_arbol = crear_pipeline(estimadores_base()["arbol_defecto"], X)
    r_def = evaluar(pipe_arbol, X, y, cv)                      # arbol por defecto, mismo X y mismo cv
    defecto = empaquetar(r_def, y)
    t0 = time.perf_counter()
    gs = buscar(pipe_arbol, X, y, cv)
    t_busqueda = time.perf_counter() - t0
    i = gs.best_index_
    cvr = pd.DataFrame(gs.cv_results_)
    mejor = parametros_limpios(gs.best_params_)
    n_comb = len(cvr)
    print(f"Espacio: max_depth={PARAM_GRID['modelo__max_depth']} x min_samples_leaf={PARAM_GRID['modelo__min_samples_leaf']} "
          f"= {n_comb} combinaciones x 5 pliegues = {n_comb * 5} ajustes (+1 de refit)")
    print(f"Ganadora: {mejor}")
    print(f"Arbol por defecto  : exactitud CV = {defecto['exactitud']['media']:.4f} | recall bad = {defecto['recall_bad']['media']:.4f}")
    print(f"Numero de la busqueda (optimista, best_score_): exactitud = {gs.best_score_:.4f} "
          f"| recall bad de esa combinacion = {cvr.loc[i, 'mean_test_recall_bad']:.4f}")
    print(f"Mejora de la busqueda frente al defecto (optimista): {100 * (gs.best_score_ - defecto['exactitud']['media']):+.2f} pp "
          f"| tiempo de la busqueda = {t_busqueda:.1f} s")
    top = cvr.sort_values("rank_test_exactitud").head(5)
    for _, f in top.iterrows():
        print(f"  rango {int(f.rank_test_exactitud):2d}: max_depth={f['param_modelo__max_depth']}, "
              f"min_samples_leaf={f['param_modelo__min_samples_leaf']} -> exactitud {f.mean_test_exactitud:.4f} "
              f"(DE {f.std_test_exactitud:.4f}), recall bad {f.mean_test_recall_bad:.4f}")
    out["busqueda"] = {
        "mejores_parametros": {k: ("None" if v is None else v) for k, v in mejor.items()},
        "exactitud_busqueda_optimista": float(gs.best_score_),
        "recall_bad_busqueda_optimista": float(cvr.loc[i, "mean_test_recall_bad"]),
        "defecto": defecto, "tiempo_busqueda_s": t_busqueda,
        "mejora_optimista_pp": float(100 * (gs.best_score_ - defecto["exactitud"]["media"])),
        "resultados": [
            {"max_depth": ("None" if f["param_modelo__max_depth"] is None or pd.isna(f["param_modelo__max_depth"]) else int(f["param_modelo__max_depth"])),
             "min_samples_leaf": int(f["param_modelo__min_samples_leaf"]),
             "exactitud_media": float(f.mean_test_exactitud), "exactitud_desv": float(f.std_test_exactitud),
             "recall_bad_media": float(f.mean_test_recall_bad), "rango_exactitud": int(f.rank_test_exactitud)}
            for _, f in cvr.iterrows()],
    }

    # ---- 2. Numero honesto: validacion cruzada anidada ----
    print("\n== 2. Medicion honesta: validacion cruzada anidada (busqueda DENTRO de cada pliegue externo) ==")
    t0 = time.perf_counter()
    r_anid = validacion_anidada(pipe_arbol, X, y, cv)
    t_anid = time.perf_counter() - t0
    anidada = empaquetar(r_anid, y)
    por_pliegue = [{"parametros": {k: ("None" if v is None else v) for k, v in parametros_limpios(m.best_params_).items()},
                    "exactitud_interna": float(m.best_score_)} for m in r_anid["modelos_ajustados"]]
    for k, p in enumerate(por_pliegue, 1):
        print(f"  pliegue externo {k}: ganadora {p['parametros']} | exactitud interna {p['exactitud_interna']:.4f} "
              f"| exactitud externa {r_anid['exactitud_por_pliegue'][k - 1]:.4f}")
    print(f"Anidada (honesta): exactitud = {anidada['exactitud']['media']:.4f} +/- {anidada['exactitud']['desv']:.4f} "
          f"| recall bad = {anidada['recall_bad']['media']:.4f} +/- {anidada['recall_bad']['desv']:.4f} "
          f"| tiempo total = {t_anid:.1f} s")
    opt = gs.best_score_ - anidada["exactitud"]["media"]
    print(f"Optimismo de la busqueda: {gs.best_score_:.4f} (busqueda) - {anidada['exactitud']['media']:.4f} (anidada) = {100 * opt:+.2f} pp")
    print(f"Mejora HONESTA frente al defecto: {anidada['exactitud']['media']:.4f} - {defecto['exactitud']['media']:.4f} = "
          f"{100 * (anidada['exactitud']['media'] - defecto['exactitud']['media']):+.2f} pp")
    out["anidada"] = {**anidada, "por_pliegue_externo": por_pliegue, "tiempo_total_s": t_anid,
                      "optimismo_busqueda_pp": float(100 * opt),
                      "mejora_honesta_pp": float(100 * (anidada["exactitud"]["media"] - defecto["exactitud"]["media"]))}

    # Tiempo de ajustar UNA vez la configuracion ganadora (sin busqueda), para comparar costo computacional.
    arbol_final = clone(pipe_arbol).set_params(**gs.best_params_)
    r_final = evaluar(arbol_final, X, y, cv)
    out["arbol_config_final_sin_busqueda"] = {
        "tiempo_ajuste_s": resumen(r_final["tiempo_ajuste_por_pliegue_s"]),
        "nota": "Exactitud de esta configuracion con CV simple = numero optimista; solo se usa su tiempo de ajuste."}

    # ---- 3. Comparacion de tres modelos con el mismo protocolo ----
    print("\n== 3. Tres modelos, mismo X, misma y, misma validacion cruzada externa ==")
    modelos = {"arbol_afinado": anidada}
    for clave in ("random_forest", "boosting_hgb"):
        modelos[clave] = empaquetar(evaluar(crear_pipeline(estimadores_base()[clave], X), X, y, cv), y)
    out["comparacion"] = {"arbol_defecto": defecto, **modelos}
    out["comparacion"]["notas"] = {
        "arbol_afinado": "validacion anidada (honesta); el tiempo incluye la busqueda completa dentro de cada pliegue",
        "random_forest": "parametros por defecto (no se afino): no hay seleccion de hiperparametros que sesgue la medicion",
        "boosting_hgb": "parametros por defecto (no se afino): no hay seleccion de hiperparametros que sesgue la medicion"}
    for clave in ("arbol_defecto", "arbol_afinado", "random_forest", "boosting_hgb"):
        m = out["comparacion"][clave]
        mx = m["matriz_fuera_de_pliegue"]
        print(f"{NOMBRES[clave]:22s} exactitud {m['exactitud']['media']:.4f} +/- {m['exactitud']['desv']:.4f} | "
              f"malos detectados {m['recall_bad']['media']:.4f} +/- {m['recall_bad']['desv']:.4f} | "
              f"ajuste {m['tiempo_ajuste_s']['media']:.3f} s/pliegue | "
              f"matriz TN={mx['TN']} FP={mx['FP']} FN={mx['FN']} TP={mx['TP']}")
    print(f"Linea base 'siempre bueno' = {base:.4f}")

    # ---- 4. Sensibilidad: que cuesta excluir las variables sensibles (20 variables, como la Tarea 6.1) ----
    print("\n== 4. Sensibilidad: mismos modelos con las 20 variables (incluye edad y estado civil) ==")
    sens = {}
    for clave, est in estimadores_base().items():
        r = evaluar(crear_pipeline(est, X_todas), X_todas, y, cv)
        sens[clave] = {"exactitud": resumen(r["exactitud_por_pliegue"]), "recall_bad": resumen(r["recall_bad_por_pliegue"])}
        print(f"{NOMBRES[clave]:22s} exactitud {sens[clave]['exactitud']['media']:.4f} | malos detectados "
              f"{sens[clave]['recall_bad']['media']:.4f}")
    out["sensibilidad_20_variables"] = sens

    SALIDA.mkdir(exist_ok=True)
    (SALIDA / "busqueda_comparacion.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    escribir_md(out)
    print("\nOK: evidencia/busqueda_comparacion.json y .md")


def escribir_md(o):
    d, b, a, c = o["datos"], o["busqueda"], o["anidada"], o["comparacion"]
    L = ["# Busqueda de hiperparametros y comparacion de modelos (Tarea 6.2)", "",
         "Generado por `src/busqueda_comparacion.py`; todas las cifras salen de `busqueda_comparacion.json`.", "",
         f"- Datos: {d['filas']} filas; bad={d['bad']}, good={d['good']}; linea base «siempre bueno» = {d['linea_base_siempre_bueno']:.4f}.",
         f"- Predictoras ({len(d['predictoras'])}): sin {', '.join(d['excluidas_por_sensibles'])} (variables sensibles, solo para auditar).",
         f"- CV externa: `{o['protocolo']['cv_externa']}`; CV interna: `{o['protocolo']['cv_interna_busqueda']}`.", "",
         "## 1. Busqueda", "",
         f"Espacio: {o['protocolo']['param_grid']} = {o['protocolo']['combinaciones']} combinaciones.",
         f"Ganadora: {b['mejores_parametros']}.", "",
         "| Medicion | Exactitud | Malos detectados |", "|---|---|---|",
         f"| Arbol por defecto (CV) | {b['defecto']['exactitud']['media']:.4f} | {b['defecto']['recall_bad']['media']:.4f} |",
         f"| Numero de la busqueda (optimista) | {b['exactitud_busqueda_optimista']:.4f} | {b['recall_bad_busqueda_optimista']:.4f} |",
         f"| Anidada (honesta) | {a['exactitud']['media']:.4f} | {a['recall_bad']['media']:.4f} |", "",
         f"Mejora optimista: {b['mejora_optimista_pp']:+.2f} pp. Mejora honesta: {a['mejora_honesta_pp']:+.2f} pp. "
         f"Optimismo de la busqueda: {a['optimismo_busqueda_pp']:+.2f} pp.", "",
         "## 2. Comparacion con el mismo protocolo", "",
         "| Modelo | Exactitud M (DE) | Malos detectados M (DE) | Ajuste (s/pliegue) |", "|---|---|---|---|"]
    for clave in ("arbol_defecto", "arbol_afinado", "random_forest", "boosting_hgb"):
        m = c[clave]
        L.append(f"| {NOMBRES[clave]} | {m['exactitud']['media']:.4f} ({m['exactitud']['desv']:.4f}) | "
                 f"{m['recall_bad']['media']:.4f} ({m['recall_bad']['desv']:.4f}) | {m['tiempo_ajuste_s']['media']:.3f} |")
    (SALIDA / "busqueda_comparacion.md").write_text("\n".join(L) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
