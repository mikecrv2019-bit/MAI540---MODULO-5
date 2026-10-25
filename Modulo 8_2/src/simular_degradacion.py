"""Simulacion de degradacion (Tarea 8.2): el mismo modelo, los mismos lotes, pero medidos de otra manera.

    python src/simular_degradacion.py

Adaptado de ejemplo_degradacion del Modulo 8. Se entrena la regresion logistica con el 75 % de los lotes y se evalua con el
25 % restante en dos mundos: el original y uno donde la medicion cambio (otro metodo de laboratorio o mas ruido). Se repite con
100 repartos distintos para no depender de uno. No cambia ni una linea del modelo: solo cambian los datos que recibe.

Escenarios (todos son supuestos, no hechos medidos en Dilitio Wine Corp):
  - sesgo de metodo: la prolina (y a veces el magnesio) se leen un X % mas altas por un metodo o instrumento distinto.
  - ruido: cada medicion recibe un error aleatorio de tamano k desviaciones estandar de esa variable.
Por escenario se reporta: exactitud, % de lotes fuera de rango y % de repartos donde salta cada senal de deriva
(distribucion o rango, ver deriva.py). En 'sin cambio' esos porcentajes son la tasa de falsas alarmas.
"""
import json
import warnings

import numpy as np
from sklearn.base import clone
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from datos import PREDICTORAS, RAIZ, cargar_datos
from deriva import reporte_deriva
from modelos import crear_modelos

EVIDENCIA = RAIZ / "evidencia"
N_REPARTOS = 100
MODELO = "regresion_logistica"

# nombre -> (sesgo multiplicativo por variable, ruido en desviaciones estandar)
ESCENARIOS = {
    "sin cambio": ({}, 0.0),
    "prolina +10 %": ({"proline": 1.10}, 0.0),
    "prolina +25 %": ({"proline": 1.25}, 0.0),
    "prolina +50 %": ({"proline": 1.50}, 0.0),
    "prolina y magnesio +25 %": ({"proline": 1.25, "magnesium": 1.25}, 0.0),
    "ruido 0.5 desv.": ({}, 0.5),
    "ruido 1.0 desv.": ({}, 1.0),
}


def aplicar_escenario(X, sesgo, ruido, rng, desv_ref):
    """Devuelve una copia de X con el sesgo multiplicativo y el ruido aplicados. `desv_ref`: desviaciones del entrenamiento."""
    X2 = X.copy()
    for col, factor in sesgo.items():
        X2[col] = X2[col] * factor
    if ruido:
        X2[PREDICTORAS] = X2[PREDICTORAS] + rng.normal(0.0, ruido * desv_ref.to_numpy(), X2[PREDICTORAS].shape)
    return X2


def simular(n_repartos=N_REPARTOS, escenarios=ESCENARIOS):
    X, y = cargar_datos()
    estimador = crear_modelos()[MODELO]
    acc = {e: [] for e in escenarios}
    fuera = {e: [] for e in escenarios}
    alerta_ks = {e: [] for e in escenarios}
    alerta_rango = {e: [] for e in escenarios}
    for semilla in range(n_repartos):
        X_ent, X_val, y_ent, y_val = train_test_split(X, y, test_size=0.25, stratify=y, random_state=semilla)
        modelo = clone(estimador).fit(X_ent, y_ent)
        rng = np.random.default_rng(1000 + semilla)
        desv = X_ent.std(ddof=1)
        for nombre, (sesgo, ruido) in escenarios.items():
            X_nuevo = aplicar_escenario(X_val, sesgo, ruido, rng, desv)
            acc[nombre].append(accuracy_score(y_val, modelo.predict(X_nuevo)))
            rep = reporte_deriva(X_ent, X_nuevo)
            fuera[nombre].append(rep["lotes_con_valores_fuera_de_rango"] / rep["lotes"])
            alerta_ks[nombre].append(rep["alerta_distribucion"])
            alerta_rango[nombre].append(rep["alerta_rango"])
    return {
        "n_repartos": n_repartos, "lotes_entrenamiento": len(X_ent), "lotes_evaluacion": len(X_val),
        "escenarios": {
            e: {"exactitud_media": float(np.mean(acc[e])), "exactitud_desv": float(np.std(acc[e], ddof=1)),
                "lotes_fuera_de_rango": float(np.mean(fuera[e])), "alerta_distribucion": float(np.mean(alerta_ks[e])),
                "alerta_rango": float(np.mean(alerta_rango[e])),
                "alerta_cualquiera": float(np.mean(np.logical_or(alerta_ks[e], alerta_rango[e])))}
            for e in escenarios
        },
    }


def _markdown(r):
    base = r["escenarios"]["sin cambio"]["exactitud_media"]
    L = ["# Simulacion de degradacion (generado por `src/simular_degradacion.py`)", "",
         f"Regresion logistica entrenada con {r['lotes_entrenamiento']} lotes y evaluada con {r['lotes_evaluacion']}, en "
         f"{r['n_repartos']} repartos distintos. Los cambios son supuestos, no mediciones reales.", "",
         "| Escenario | Exactitud (media ± desv.) | Caida | Lotes fuera de rango | Alerta por distribucion (KS) | Alerta por rango | Alguna alerta |",
         "|---|---|---|---|---|---|---|"]
    for e, v in r["escenarios"].items():
        L.append(f"| {e} | {v['exactitud_media']:.3f} ± {v['exactitud_desv']:.3f} | {base - v['exactitud_media']:.3f} | "
                 f"{v['lotes_fuera_de_rango']:.0%} | {v['alerta_distribucion']:.0%} | {v['alerta_rango']:.0%} | "
                 f"{v['alerta_cualquiera']:.0%} |")
    L += ["", "Las columnas de alerta son el % de repartos en que salta cada senal. En la fila 'sin cambio' son falsas alarmas. "
              "Distribucion: alguna variable cambia (KS con Bonferroni). Rango: mas del 30 % de los lotes sale del rango de "
              "entrenamiento.", ""]
    return "\n".join(L)


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    resultados = simular()
    EVIDENCIA.mkdir(exist_ok=True)
    (EVIDENCIA / "degradacion.json").write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")
    (EVIDENCIA / "degradacion.md").write_text(_markdown(resultados), encoding="utf-8")
    print(_markdown(resultados))
