"""Etapa 2 · Curvas de aprendizaje (diagnostico 6.1 reconstruido frente a la 6.2) y auditoria por subgrupo.

Uso:  python src/curvas_auditoria.py      (requiere haber corrido busqueda_comparacion.py)
Escribe evidencia/curvas.json, evidencia/auditoria_subgrupos.json/.md y figs/*.png.
"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.base import clone

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auditoria import MIN_POSITIVOS, UMBRAL_DISPARIDAD, recall_por_subgrupo
from busqueda import crear_busqueda
from config import MODELO_ELEGIDO
from curvas import curva_aprendizaje, graficar, resumen_curva
from datos import RAIZ, SUBGRUPOS_AUDITORIA, cargar_datos, grupos_auditoria, predictoras
from interpretabilidad import importancia_por_permutacion
from modelos import NOMBRES, crear_pipeline, estimadores_base
from validacion import SEMILLA_CV_INTERNA, crear_cv, evaluar, linea_base_siempre_bueno, matriz_y_metricas

EVID = RAIZ / "evidencia"
FIGS = RAIZ / "figs"


def modelo_elegido(X):
    """Estimador del modelo elegido tal como se evaluo en la comparacion (arbol afinado = busqueda anidada)."""
    if MODELO_ELEGIDO == "arbol_afinado":
        return crear_busqueda(crear_pipeline(estimadores_base()["arbol_defecto"], X), crear_cv(SEMILLA_CV_INTERNA))
    return crear_pipeline(estimadores_base()[MODELO_ELEGIDO], X)


def main():
    X_todas, y = cargar_datos()
    X = predictoras(X_todas)
    cv = crear_cv()
    base = linea_base_siempre_bueno(y)
    previo = json.loads((EVID / "busqueda_comparacion.json").read_text(encoding="utf-8"))
    base_est = estimadores_base()

    # ---------- Curvas de aprendizaje ----------
    print("== Curvas de aprendizaje (misma CV: StratifiedKFold(5, shuffle, 42); 10 tamanos de 80 a 800 casos) ==")
    # Arbol afinado: se fija la configuracion ganadora de la busqueda (diagnostico de una configuracion, no una medicion de rendimiento).
    gan = {k: (None if v == "None" else v) for k, v in previo["busqueda"]["mejores_parametros"].items()}
    arbol_afinado = crear_pipeline(base_est["arbol_defecto"], X).set_params(**{f"modelo__{k}": v for k, v in gan.items()})
    casos = {
        "arbol_6_1_diagnostico": ("Árbol por defecto, 20 variables (6.1)", crear_pipeline(base_est["arbol_defecto"], X_todas), X_todas),
        "rf_6_1_diagnostico": ("Random Forest por defecto, 20 variables (6.1)", crear_pipeline(base_est["random_forest"], X_todas), X_todas),
        "arbol_afinado": ("Árbol afinado, 18 variables", arbol_afinado, X),
        "random_forest": ("Random Forest, 18 variables", crear_pipeline(base_est["random_forest"], X), X),
        "boosting_hgb": ("HistGradientBoosting, 18 variables", crear_pipeline(base_est["boosting_hgb"], X), X),
        "boosting_hgb_20_variables": ("HistGradientBoosting, 20 variables (control)", crear_pipeline(base_est["boosting_hgb"], X_todas), X_todas),
    }
    curvas = {}
    for clave, (etiqueta, pipe, Xc) in casos.items():
        t, ent, val = curva_aprendizaje(pipe, Xc, y, cv)
        r = resumen_curva(t, ent, val)
        r["etiqueta"] = etiqueta
        curvas[clave] = r
        print(f"{etiqueta:48s} entrenamiento {r['entrenamiento_final']:.4f} | validacion {r['validacion_final']:.4f} "
              f"| brecha {r['entrenamiento_final']:.4f} - {r['validacion_final']:.4f} = {r['brecha_final']:.4f} "
              f"| pendiente validacion ({r['tamano_inicio_tramo']}-{r['tamanos'][-1]} casos): {r['pendiente_validacion_pp_por_100_casos']:+.2f} pp por 100 casos")
    (EVID / "curvas.json").write_text(json.dumps(curvas, indent=2, ensure_ascii=False), encoding="utf-8")
    FIGS.mkdir(exist_ok=True)
    graficar([("Árbol por defecto\n(6.1, 20 var.)", curvas["arbol_6_1_diagnostico"]),
              ("Random Forest por defecto\n(6.1, 20 var.)", curvas["rf_6_1_diagnostico"]),
              (f"{NOMBRES[MODELO_ELEGIDO]}\n(6.2, 18 var.)", curvas[MODELO_ELEGIDO])],
             FIGS / "curva_elegido_vs_diagnostico.png", base=base)
    graficar([(casos[k][0].replace(", ", "\n"), curvas[k]) for k in casos], FIGS / "curvas_todas.png", base=base)

    # ---------- Auditoria por subgrupo del modelo elegido ----------
    print(f"\n== Auditoria por subgrupo: {NOMBRES[MODELO_ELEGIDO]} (predicciones fuera de pliegue, misma CV) ==")
    est = modelo_elegido(X)
    res = evaluar(est, X, y, cv)
    pred = res["prediccion_fuera_de_pliegue"]
    mx = matriz_y_metricas(y, pred)
    print(f"Matriz de confusion (positiva = bad): TN={mx['TN']} FP={mx['FP']} FN={mx['FN']} TP={mx['TP']}")
    print(f"exactitud = (TP+TN)/total = ({mx['TP']}+{mx['TN']})/{len(y)} = {mx['exactitud']:.4f}")
    print(f"recall bad = TP/(TP+FN) = {mx['TP']}/({mx['TP']}+{mx['FN']}) = {mx['recall_bad']:.4f}")
    print(f"precision bad = TP/(TP+FP) = {mx['TP']}/({mx['TP']}+{mx['FP']}) = {mx['precision_bad']:.4f}")
    print(f"linea base 'siempre bueno' = {base:.4f}")
    grupos = grupos_auditoria(X_todas)
    tablas, recall_global = [], None
    print(f"Metrica prioritaria: recall de bad. Umbral |recall_subgrupo - recall_global| <= {UMBRAL_DISPARIDAD}; "
          f"minimo {MIN_POSITIVOS} positivos (bad) por subgrupo")
    for col in SUBGRUPOS_AUDITORIA:
        tabla, recall_global = recall_por_subgrupo(y, pred, grupos, col)
        tablas.append(tabla)
        print(f"-- {col} (recall global = {recall_global:.4f})")
        for _, f in tabla.iterrows():
            estado = ("SUPERA umbral" if f.supera_umbral else "dentro del umbral") if f.evaluable else f"no evaluable (< {MIN_POSITIVOS} bad)"
            print(f"   {f.valor:20s} n={f.n:4d} bad={f.positivos_bad:3d} TP={f.aciertos_bad:3d} recall={f.recall_bad:.4f} "
                  f"dif={f.recall_bad:.4f}-{recall_global:.4f}={f.dif_vs_global:+.4f} exactitud={f.exactitud:.4f} -> {estado}")
    import pandas as pd
    tabla_total = pd.concat(tablas, ignore_index=True)
    sup = tabla_total[tabla_total.supera_umbral]
    print(f"Subgrupos evaluables que superan el umbral: {len(sup)} de {int(tabla_total.evaluable.sum())} evaluables")
    out = {"modelo": MODELO_ELEGIDO, "matriz_fuera_de_pliegue": mx, "recall_global": recall_global,
           "umbral": UMBRAL_DISPARIDAD, "min_positivos": MIN_POSITIVOS,
           "subgrupos": tabla_total.to_dict(orient="records")}
    (EVID / "auditoria_subgrupos.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    L = [f"# Auditoria por subgrupo: {NOMBRES[MODELO_ELEGIDO]}", "",
         "Predicciones fuera de pliegue (CV estratificada de 5, semilla 42). Variables sensibles solo para agrupar.", "",
         f"Recall global de bad = {recall_global:.4f}. Umbral {UMBRAL_DISPARIDAD}; minimo {MIN_POSITIVOS} positivos.", "",
         "| Subgrupo | Valor | n | bad | Recall bad | Dif. vs global | Exactitud | Estado |", "|---|---|---|---|---|---|---|---|"]
    for _, f in tabla_total.iterrows():
        estado = ("supera umbral" if f.supera_umbral else "dentro") if f.evaluable else "no evaluable"
        L.append(f"| {f.subgrupo} | {f.valor} | {f.n} | {f.positivos_bad} | {f.recall_bad:.4f} | {f.dif_vs_global:+.4f} | {f.exactitud:.4f} | {estado} |")
    (EVID / "auditoria_subgrupos.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    # ---------- Interpretabilidad: que variables usa el modelo elegido ----------
    print(f"\n== Interpretabilidad: importancia por permutacion de {NOMBRES[MODELO_ELEGIDO]} (caida de exactitud en prueba) ==")
    imp = importancia_por_permutacion(modelo_elegido(X), X, y, cv)
    for _, f in imp.head(8).iterrows():
        print(f"   {f.variable:26s} caida = {f.caida_exactitud_media:+.4f} (DE entre pliegues {f.desv_entre_pliegues:.4f})")
    (EVID / "importancia_permutacion.json").write_text(json.dumps(imp.to_dict(orient="records"), indent=2, ensure_ascii=False), encoding="utf-8")
    print("\nOK: evidencia/curvas.json, evidencia/auditoria_subgrupos.json/.md, evidencia/importancia_permutacion.json y figs/")


if __name__ == "__main__":
    main()
