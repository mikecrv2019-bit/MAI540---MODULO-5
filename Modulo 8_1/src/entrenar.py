"""Corre el flujo completo de principio a fin y guarda la evidencia.

    python src/entrenar.py

Pasos: cargar y validar -> apartar prueba final -> CV 5x3 de linea base y 4 modelos -> criterio de seleccion ->
una sola medicion en la prueba final -> analisis de errores por categoria -> K-Means exploratorio ->
ajuste del modelo elegido con todos los lotes y guardado en modelos/modelo_final.joblib.
"""
import json
from pathlib import Path

import joblib
from sklearn.base import clone

from datos import RAIZ, cargar_datos
from errores import analisis_por_categoria
from modelos import LINEA_BASE, crear_modelos
from segmentacion import segmentar
from seleccion import elegir_modelo
from validacion import dividir, evaluar_cv, evaluar_prueba

EVIDENCIA = RAIZ / "evidencia"
RUTA_MODELO = RAIZ / "modelos" / "modelo_final.joblib"


def comparar_modelos(X_tr, y_tr):
    """CV de todos los modelos (linea base incluida) con el mismo X, y y la misma validacion cruzada."""
    return {nombre: evaluar_cv(est, X_tr, y_tr) for nombre, est in crear_modelos().items()}


def ejecutar():
    X, y = cargar_datos()
    X_tr, X_te, y_tr, y_te = dividir(X, y)
    modelos = crear_modelos()

    cv = comparar_modelos(X_tr, y_tr)
    decision = elegir_modelo(cv)
    elegido = decision["elegido"]

    prueba = {n: evaluar_prueba(modelos[n], X_tr, y_tr, X_te, y_te) for n in (LINEA_BASE, elegido)}
    errores_cv = analisis_por_categoria(y_tr, list(cv[elegido]["prediccion_fuera_de_pliegue"]))
    errores_prueba = analisis_por_categoria(y_te, prueba[elegido]["prediccion"])
    mal_clasificados = [int(i) for i in X_te.index[prueba[elegido]["prediccion"] != y_te.to_numpy()]]

    resultados = {
        "datos": {"filas": len(X), "predictoras": X.shape[1], "entrenamiento": len(X_tr), "prueba": len(X_te),
                  "distribucion": {k: int(v) for k, v in y.value_counts().sort_index().items()}},
        "validacion_cruzada": {n: {k: r[k] for k in ("exactitud", "f1_macro", "exactitud_por_pliegue",
                                                       "f1_macro_por_pliegue")} for n, r in cv.items()},
        "seleccion": decision,
        "prueba_final": {n: {"exactitud": p["exactitud"], "f1_macro": p["f1_macro"]} for n, p in prueba.items()},
        "errores_validacion_cruzada": errores_cv,
        "errores_prueba_final": errores_prueba,
        "filas_mal_clasificadas_en_prueba": mal_clasificados,
        "segmentacion_kmeans": segmentar(X_tr, y_tr, X_te, y_te),
    }

    EVIDENCIA.mkdir(exist_ok=True)
    (EVIDENCIA / "resultados.json").write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    (EVIDENCIA / "resultados.md").write_text(_markdown(resultados), encoding="utf-8")

    final = clone(modelos[elegido]).fit(X, y)  # para uso: ajustado con los 178 lotes
    RUTA_MODELO.parent.mkdir(exist_ok=True)
    joblib.dump({"nombre": elegido, "modelo": final, "columnas": list(X.columns),
                 "minimos": X.min().to_dict(), "maximos": X.max().to_dict()}, RUTA_MODELO)
    return resultados


def _markdown(r):
    L = ["# Resultados del capstone (generado por `src/entrenar.py`)", ""]
    d = r["datos"]
    L += [f"Lotes: {d['filas']} ({d['entrenamiento']} entrenamiento / {d['prueba']} prueba final). "
          f"Distribucion: {d['distribucion']}.", "",
          "## Validacion cruzada 5 pliegues x 3 repeticiones (solo entrenamiento)", "",
          "| Modelo | Exactitud (media ± desv.) | F1 macro (media ± desv.) |", "|---|---|---|"]
    for n, v in r["validacion_cruzada"].items():
        L.append(f"| {n} | {v['exactitud']['media']:.3f} ± {v['exactitud']['desv']:.3f} | "
                 f"{v['f1_macro']['media']:.3f} ± {v['f1_macro']['desv']:.3f} |")
    s = r["seleccion"]
    L += ["", f"**Regla:** {s['regla']}", "",
          f"**Elegido:** `{s['elegido']}` (mejor por media: `{s['mejor_por_media']}`; "
          f"piso de equivalencia {s['piso_de_equivalencia']:.3f}; equivalentes: {s['equivalentes']}).", "",
          "## Prueba final (una sola medicion)", "", "| Modelo | Exactitud | F1 macro |", "|---|---|---|"]
    for n, v in r["prueba_final"].items():
        L.append(f"| {n} | {v['exactitud']:.3f} | {v['f1_macro']:.3f} |")
    for titulo, clave in (("Errores por categoria, predicciones fuera de pliegue (entrenamiento)", "errores_validacion_cruzada"),
                          ("Errores por categoria, prueba final", "errores_prueba_final")):
        e = r[clave]
        L += ["", f"## {titulo}", "", f"Errores: {e['errores']} de {e['total']}.", "",
              "| Clase | n | Recall | Precision | F1 |", "|---|---|---|---|---|"]
        for c, m in e["por_clase"].items():
            L.append(f"| {c} | {m['n']} | {m['recall']:.3f} | {m['precision']:.3f} | {m['f1']:.3f} |")
        pares = ", ".join(f"{c['real']} → {c['predicho']}: {c['n']}" for c in e["confusiones"]) or "ninguna"
        L += ["", f"Confusiones (real → predicho): {pares}."]
    k = r["segmentacion_kmeans"]
    L += ["", "## K-Means exploratorio (k = 3)", "",
          f"- Ajustado solo con el entrenamiento ({k['ajustado_con']} lotes). Silueta: {k['silueta']:.4f} (piloto {k['silueta_piloto']}).",
          f"- Estabilidad (ARI en {k['estabilidad_ari']['n_remuestreos']} remuestreos): "
          f"{k['estabilidad_ari']['media']:.3f} ± {k['estabilidad_ari']['desv']:.3f} (min {k['estabilidad_ari']['min']:.3f}).",
          f"- Acuerdo con `cultivar` (ARI): {k['ari_vs_cultivar_entrenamiento']:.3f} en entrenamiento, "
          f"{k['ari_vs_cultivar_prueba']:.3f} en la prueba final (filas que K-Means no vio).", ""]
    return "\n".join(L)


if __name__ == "__main__":
    resultados = ejecutar()
    print((EVIDENCIA / "resultados.md").read_text(encoding="utf-8"))
    print(f"Modelo guardado en {Path(RUTA_MODELO).relative_to(RAIZ)}")
