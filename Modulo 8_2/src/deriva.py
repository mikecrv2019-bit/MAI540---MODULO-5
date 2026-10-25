"""Deteccion de deriva: compara un lote de mediciones nuevas contra los datos con que se entreno el modelo.

El modelo no avisa cuando el mundo cambia (por ejemplo, un laboratorio nuevo mide la prolina con otro metodo). Dos senales:
  1. Rango: cuantos lotes tienen algun valor fuera del minimo-maximo visto en el entrenamiento.
  2. Distribucion: prueba de Kolmogorov-Smirnov de dos muestras por variable, con correccion de Bonferroni
     (13 variables a la vez: sin correccion saltarian falsas alarmas con frecuencia).
Ninguna de las dos necesita saber la clase real del lote; la caida de la exactitud solo se ve con lotes etiquetados.

Son complementarias (simular_degradacion.py): la prueba KS detecta un corrimiento de la media (otro metodo de medicion) pero
casi no ve el ruido; el rango ve el ruido. El rango por si solo no sirve con un umbral bajo: con 13 variables, alrededor del
15 % de los lotes normales tiene algun valor fuera del minimo-maximo del entrenamiento, asi que el umbral es 30 %.
"""
import numpy as np
from scipy.stats import ks_2samp

from datos import PREDICTORAS

MIN_LOTES_KS = 20   # con menos lotes la prueba casi nunca detecta nada: solo se mira el rango
ALFA = 0.05
UMBRAL_FUERA_DE_RANGO = 0.30   # el doble del ~15 % que sale de rango sin que nada haya cambiado


def reporte_deriva(X_ref, X_nuevo, alfa=ALFA):
    """Resumen de deriva de `X_nuevo` frente a `X_ref` (ambos DataFrames con las 13 variables)."""
    n = len(X_nuevo)
    if n == 0:
        raise ValueError("No hay lotes para comparar.")
    minimos, maximos = X_ref[PREDICTORAS].min(), X_ref[PREDICTORAS].max()
    fuera = (X_nuevo[PREDICTORAS] < minimos) | (X_nuevo[PREDICTORAS] > maximos)
    usa_ks = n >= MIN_LOTES_KS
    umbral = alfa / len(PREDICTORAS)
    variables = []
    for c in PREDICTORAS:
        fila = {"variable": c, "lotes_fuera_de_rango": int(fuera[c].sum()), "ks": None, "p": None, "deriva": False}
        if usa_ks:
            res = ks_2samp(X_ref[c], X_nuevo[c])
            fila.update(ks=float(res.statistic), p=float(res.pvalue), deriva=bool(res.pvalue < umbral))
        variables.append(fila)
    con_deriva = [v["variable"] for v in variables if v["deriva"]]
    lotes_fuera = int(fuera.any(axis=1).sum())
    return {
        "lotes": n,
        "lotes_con_valores_fuera_de_rango": lotes_fuera,
        "ks_aplicado": usa_ks,
        "variables_con_deriva": con_deriva,
        "alerta_distribucion": bool(con_deriva),
        "alerta_rango": lotes_fuera / n > UMBRAL_FUERA_DE_RANGO,
        "alerta": bool(con_deriva) or lotes_fuera / n > UMBRAL_FUERA_DE_RANGO,
        "variables": variables,
    }


def mensaje_deriva(reporte):
    """Texto corto para la persona que usa la herramienta."""
    r = reporte
    partes = [f"{r['lotes_con_valores_fuera_de_rango']} de {r['lotes']} lotes tienen algun valor fuera del rango de entrenamiento."]
    if r["ks_aplicado"]:
        partes.append("Variables cuya distribucion cambio: " + (", ".join(r["variables_con_deriva"]) or "ninguna") + ".")
    else:
        partes.append(f"Con menos de {MIN_LOTES_KS} lotes no se compara la distribucion; solo el rango.")
    partes.append("ALERTA: los datos no se parecen a los del entrenamiento; no confie en las predicciones sin reevaluar."
                  if r["alerta"] else "Sin senales de deriva.")
    return " ".join(partes)
