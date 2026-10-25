"""Uso de la herramienta: clasifica un lote de vino segun su perfil quimico (class_0, class_1 o class_2).

    python src/predecir.py --fila 0                  # un lote del archivo de datos (demostracion)
    python src/predecir.py --json mi_lote.json       # un lote propio: JSON con las 13 variables

Requiere haber corrido antes  python src/entrenar.py  (crea modelos/modelo_final.joblib).
El resultado es un PERFIL quimico, no una decision comercial: la asignacion perfil -> linea de producto
(entrada, revision de proceso, premium) debe definirla Dilitio Wine Corp.
"""
import argparse
import json
import math

import joblib
import pandas as pd

from datos import PREDICTORAS, RAIZ, RUTA_DATOS, cargar_datos
from entrenar import RUTA_MODELO


def cargar_modelo(ruta=RUTA_MODELO):
    if not ruta.exists():
        raise FileNotFoundError(f"No existe {ruta.relative_to(RAIZ)}. Ejecute primero:  python src/entrenar.py")
    return joblib.load(ruta)


def clasificar_lote(valores, ruta=RUTA_MODELO):
    """Clasifica un lote dado como {variable: valor} con las 13 variables quimicas.

    Falla si falta una variable, sobra una o algun valor no es un numero finito. Si un valor cae fuera del rango
    visto en el entrenamiento, el lote se clasifica igual pero se devuelve una advertencia: el modelo extrapola.
    """
    faltan = [c for c in PREDICTORAS if c not in valores]
    sobran = sorted(set(valores) - set(PREDICTORAS))
    if faltan or sobran:
        raise ValueError(f"Variables del lote invalidas. Faltan: {faltan}. Sobran: {sobran}.")
    for c in PREDICTORAS:
        v = valores[c]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError(f"'{c}' debe ser un numero finito, recibido: {v!r}")

    guardado = cargar_modelo(ruta)
    modelo = guardado["modelo"]
    X = pd.DataFrame([{c: float(valores[c]) for c in PREDICTORAS}], columns=PREDICTORAS)
    advertencias = [
        f"{c}={valores[c]} fuera del rango de entrenamiento [{guardado['minimos'][c]}, {guardado['maximos'][c]}]"
        for c in PREDICTORAS if not guardado["minimos"][c] <= valores[c] <= guardado["maximos"][c]
    ]
    probabilidades = modelo.predict_proba(X)[0]
    return {
        "perfil": str(modelo.predict(X)[0]),
        "probabilidades": {str(c): round(float(p), 4) for c, p in zip(modelo.classes_, probabilidades)},
        "modelo": guardado["nombre"],
        "advertencias": advertencias,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--fila", type=int, help="indice (0-177) de un lote de datos/wine.csv")
    g.add_argument("--json", help="archivo JSON con las 13 variables de un lote")
    args = ap.parse_args()
    if args.fila is not None:
        X, y = cargar_datos(RUTA_DATOS)
        if not 0 <= args.fila < len(X):
            ap.error(f"--fila debe estar entre 0 y {len(X) - 1}")
        lote, real = {c: float(v) for c, v in X.iloc[args.fila].items()}, y.iloc[args.fila]
        print(f"Lote {args.fila} del archivo de datos (cultivar registrado: {real})")
    else:
        with open(args.json, encoding="utf-8") as f:
            lote = json.load(f)
    print(json.dumps(clasificar_lote(lote), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
