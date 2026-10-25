"""Analisis de errores por categoria con los 178 lotes (Tarea 8.2): por clase, por grupo de una variable y por confianza.

    python src/detalle_errores.py

El modelo ya esta elegido (regresion logistica, Tarea 8.1): aqui NO se elige nada, solo se describe donde falla. Por eso
se pueden usar los 178 lotes: validacion cruzada estratificada 5x3 (la misma de validacion.py) en la que cada lote lo
predice un modelo que no lo vio. Cada lote queda predicho 3 veces (una por repeticion). La tabla principal usa la
primera repeticion (cada lote cuenta una vez); las otras dos solo sirven para saber si un error es estable.

Las variables de la herramienta son mediciones quimicas: no hay edad, sexo ni estado civil que auditar.
"""
import json

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import RepeatedStratifiedKFold

from datos import CLASES, PREDICTORAS, RAIZ, cargar_datos
from modelos import crear_modelos
from validacion import N_PLIEGUES, N_REPETICIONES, SEMILLA

EVIDENCIA = RAIZ / "evidencia"
MODELO = "regresion_logistica"
VARIABLES_GRUPO = ["alcohol", "proline", "magnesium"]   # alcohol: la que mas separa; prolina y magnesio: las que mas dependen del metodo
CORTES_CONFIANZA = [0.0, 0.8, 0.9, 0.99, 1.0001]


def intervalo_wilson(k, n, z=1.96):
    """Intervalo de Wilson al 95 % para una proporcion k/n (sirve con n pequeno, donde la normal falla)."""
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    mitad = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (float(max(0.0, centro - mitad)), float(min(1.0, centro + mitad)))


def predicciones_repetidas(estimador, X, y, semilla=SEMILLA):
    """Predicciones fuera de pliegue de las N_REPETICIONES repeticiones. Devuelve arreglos [repeticion, lote]."""
    cv = RepeatedStratifiedKFold(n_splits=N_PLIEGUES, n_repeats=N_REPETICIONES, random_state=semilla)
    pred = np.full((N_REPETICIONES, len(y)), None, dtype=object)
    proba = np.full((N_REPETICIONES, len(y), len(CLASES)), np.nan)
    for i, (tr, te) in enumerate(cv.split(X, y)):
        modelo = clone(estimador).fit(X.iloc[tr], y.iloc[tr])
        rep = i // N_PLIEGUES
        pred[rep, te] = modelo.predict(X.iloc[te])
        proba[rep, te] = modelo.predict_proba(X.iloc[te])    # columnas en el orden de modelo.classes_ == CLASES
    if any(p is None for p in pred.ravel()) or np.isnan(proba).any():
        raise ValueError("Alguna repeticion no cubrio todos los lotes.")
    return pred, proba


def tabla_de_lotes(X, y, estimador):
    """Un renglon por lote: clase real, prediccion y confianza de la repeticion 1, y en cuantas repeticiones fallo."""
    pred, proba = predicciones_repetidas(estimador, X, y)
    reales = y.to_numpy()
    idx_real = np.array([CLASES.index(c) for c in reales])
    fallos = (pred != reales[None, :]).sum(axis=0)
    return pd.DataFrame({
        "lote": X.index,
        "real": reales,
        "predicho": pred[0],
        "confianza": proba[0].max(axis=1),
        "prob_clase_real": proba[0][np.arange(len(y)), idx_real],
        "error": pred[0] != reales,
        "repeticiones_con_error": fallos,
    }).reset_index(drop=True)


def _fila_grupo(nombre, sub):
    k, n = int(sub["error"].sum()), len(sub)
    lo, hi = intervalo_wilson(k, n)
    return {"grupo": nombre, "n": n, "errores": k, "tasa_error": k / n if n else float("nan"), "ic95": [lo, hi]}


def errores_por_clase(tabla):
    """Por clase real: n, errores, recall con su intervalo y lotes cuyo error se repite en 2 o mas repeticiones."""
    filas = []
    for c in CLASES:
        sub = tabla[tabla["real"] == c]
        f = _fila_grupo(c, sub)
        k_ok = f["n"] - f["errores"]
        f["recall"] = k_ok / f["n"]
        f["recall_ic95"] = list(intervalo_wilson(k_ok, f["n"]))
        f["errores_estables"] = int((sub["repeticiones_con_error"] >= 2).sum())
        filas.append(f)
    return filas


def errores_por_grupo(tabla, X, variable, q=3):
    """Error por tercil de una variable (grupos de igual tamano). Muestra si el error se concentra en un rango."""
    grupos = pd.qcut(X[variable].to_numpy(), q=q, labels=False, duplicates="drop")
    limites = pd.qcut(X[variable].to_numpy(), q=q, duplicates="drop", retbins=True)[1]
    filas = []
    for g in sorted(set(grupos)):
        sub = tabla[grupos == g]
        f = _fila_grupo(f"{variable} {limites[g]:.4g} a {limites[g + 1]:.4g}", sub)
        filas.append(f)
    return filas


def errores_por_confianza(tabla, cortes=CORTES_CONFIANZA):
    """Error segun la confianza (probabilidad de la clase predicha): sirve para fijar una advertencia de baja confianza."""
    filas = []
    for lo, hi in zip(cortes[:-1], cortes[1:]):
        sub = tabla[(tabla["confianza"] >= lo) & (tabla["confianza"] < hi)]
        etiqueta = f"confianza {lo:.2f} a {min(hi, 1.0):.2f}"
        filas.append(_fila_grupo(etiqueta, sub))
    return filas


def explicar_errores(X, y, tabla, top=3):
    """Para cada lote mal clasificado: en que variables se parece mas a la clase predicha que a la suya.

    Se mide con el puntaje z de la variable respecto de la media y desviacion de cada clase (con los 178 lotes).
    Es una explicacion descriptiva, no causal.
    """
    media = X.groupby(y).mean()
    desv = X.groupby(y).std(ddof=1)
    salida = []
    for _, r in tabla[tabla["error"]].iterrows():
        x = X.loc[r["lote"]]
        z_real = ((x - media.loc[r["real"]]) / desv.loc[r["real"]]).abs()
        z_pred = ((x - media.loc[r["predicho"]]) / desv.loc[r["predicho"]]).abs()
        mejora = (z_real - z_pred).sort_values(ascending=False).head(top)
        salida.append({
            "lote": int(r["lote"]), "real": r["real"], "predicho": r["predicho"],
            "confianza": round(float(r["confianza"]), 3), "prob_clase_real": round(float(r["prob_clase_real"]), 3),
            "repeticiones_con_error": int(r["repeticiones_con_error"]),
            "variables_que_lo_acercan_a_la_clase_predicha": [
                {"variable": v, "z_en_clase_real": round(float(z_real[v]), 2), "z_en_clase_predicha": round(float(z_pred[v]), 2)}
                for v in mejora.index
            ],
        })
    return salida


def ejecutar():
    X, y = cargar_datos()
    tabla = tabla_de_lotes(X, y, crear_modelos()[MODELO])
    resultados = {
        "modelo": MODELO,
        "lotes": len(tabla),
        "errores_repeticion_1": int(tabla["error"].sum()),
        "lotes_con_algun_error": int((tabla["repeticiones_con_error"] >= 1).sum()),
        "por_clase": errores_por_clase(tabla),
        "por_grupo": {v: errores_por_grupo(tabla, X, v) for v in VARIABLES_GRUPO},
        "por_confianza": errores_por_confianza(tabla),
        "lotes_mal_clasificados": explicar_errores(X, y, tabla),
        "confianza_maxima_de_un_error": float(tabla.loc[tabla["error"], "confianza"].max()) if tabla["error"].any() else None,
    }
    EVIDENCIA.mkdir(exist_ok=True)
    (EVIDENCIA / "errores_detalle.json").write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    (EVIDENCIA / "errores_detalle.md").write_text(_markdown(resultados), encoding="utf-8")
    tabla.to_csv(EVIDENCIA / "errores_por_lote.csv", index=False)
    return resultados


def _tabla(filas, extra=()):
    L = ["| Grupo | n | Errores | Tasa de error | IC 95 % (Wilson) |" + "".join(f" {e} |" for e in extra),
         "|---|---|---|---|---|" + "---|" * len(extra)]
    for f in filas:
        L.append(f"| {f['grupo']} | {f['n']} | {f['errores']} | {f['tasa_error']:.3f} | "
                 f"{f['ic95'][0]:.3f} a {f['ic95'][1]:.3f} |" + "".join(f" {f[e.lower().replace(' ', '_')]} |" for e in extra))
    return L


def _markdown(r):
    L = ["# Errores por categoria con los 178 lotes (generado por `src/detalle_errores.py`)", "",
         f"Modelo: `{r['modelo']}`. Validacion cruzada estratificada 5x3 sobre los {r['lotes']} lotes; cada lote lo predice un "
         "modelo que no lo vio. Las tablas usan la repeticion 1 (cada lote cuenta una vez).", "",
         f"Errores en la repeticion 1: **{r['errores_repeticion_1']} de {r['lotes']}**. Lotes que fallan en al menos una de las "
         f"3 repeticiones: **{r['lotes_con_algun_error']}**.", "", "## Por clase real", "",
         "| Clase | n | Errores | Recall | IC 95 % del recall | Errores estables (2 o 3 repeticiones) |", "|---|---|---|---|---|---|"]
    for f in r["por_clase"]:
        L.append(f"| {f['grupo']} | {f['n']} | {f['errores']} | {f['recall']:.3f} | "
                 f"{f['recall_ic95'][0]:.3f} a {f['recall_ic95'][1]:.3f} | {f['errores_estables']} |")
    for v, filas in r["por_grupo"].items():
        L += ["", f"## Por tercil de `{v}`", ""] + _tabla(filas)
    L += ["", "## Por confianza de la prediccion", ""] + _tabla(r["por_confianza"])
    L += ["", f"Confianza mas alta de un lote mal clasificado: {r['confianza_maxima_de_un_error']:.3f}.", "",
          "## Lotes mal clasificados (repeticion 1)", ""]
    for e in r["lotes_mal_clasificados"]:
        vs = "; ".join(f"{d['variable']} (z={d['z_en_clase_real']} en su clase, z={d['z_en_clase_predicha']} en la predicha)"
                       for d in e["variables_que_lo_acercan_a_la_clase_predicha"])
        L.append(f"- Lote {e['lote']}: real `{e['real']}`, predicho `{e['predicho']}`, confianza {e['confianza']}, "
                 f"probabilidad de su clase real {e['prob_clase_real']}, fallo en {e['repeticiones_con_error']} de 3 repeticiones. "
                 f"Se parece mas a la clase predicha en: {vs}.")
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    print((EVIDENCIA / "errores_detalle.md").read_text(encoding="utf-8") if ejecutar() else "")
