"""Criterio EXPLICITO para elegir el modelo (se fija antes de mirar la prueba final).

Metrica de decision: F1 macro de la validacion cruzada (promedia las tres clases por igual, asi la clase mas
pequena pesa lo mismo que la mayoritaria). Pasos:

1. Descartar todo modelo cuya F1 macro media no supere a la de la linea base por al menos MEJORA_MINIMA.
2. Entre los que quedan, tomar el de mayor F1 macro media; llamarlo "mejor".
3. Candidatos "equivalentes" = los que tienen media >= media(mejor) - desv(mejor)   (regla de una desviacion).
4. Elegir el MAS SIMPLE de los equivalentes segun COMPLEJIDAD (modelos.py). Si hay empate, gana el de mayor media.

Razon del paso 3-4: con 178 lotes, la diferencia entre dos modelos que quedan a menos de una desviacion es ruido;
un modelo mas simple es mas facil de explicar, auditar y mantener en Dilitio Wine Corp.
"""
from modelos import COMPLEJIDAD, LINEA_BASE

MEJORA_MINIMA = 0.10


def elegir_modelo(resultados):
    """`resultados`: {nombre: {"f1_macro": {"media", "desv"}}}. Devuelve el modelo elegido y la explicacion."""
    desconocidos = sorted(set(resultados) - {LINEA_BASE} - set(COMPLEJIDAD))
    if desconocidos:
        raise ValueError(f"Modelos sin lugar en COMPLEJIDAD (modelos.py): {desconocidos}")
    base = resultados[LINEA_BASE]["f1_macro"]["media"]
    candidatos = {n: r["f1_macro"] for n, r in resultados.items()
                  if n != LINEA_BASE and r["f1_macro"]["media"] >= base + MEJORA_MINIMA}
    descartados = sorted(n for n in resultados if n != LINEA_BASE and n not in candidatos)
    if not candidatos:
        raise ValueError(f"Ningun modelo supera a la linea base ({base:.3f}) por {MEJORA_MINIMA}.")
    mejor = max(candidatos, key=lambda n: candidatos[n]["media"])
    piso = candidatos[mejor]["media"] - candidatos[mejor]["desv"]
    equivalentes = [n for n in candidatos if candidatos[n]["media"] >= piso]
    elegido = min(equivalentes, key=lambda n: (COMPLEJIDAD.index(n), -candidatos[n]["media"]))
    return {
        "elegido": elegido,
        "mejor_por_media": mejor,
        "piso_de_equivalencia": piso,
        "equivalentes": sorted(equivalentes, key=COMPLEJIDAD.index),
        "descartados_por_linea_base": descartados,
        "regla": (f"F1 macro CV; superar la linea base por >= {MEJORA_MINIMA}; entre los modelos a menos de "
                  f"1 desviacion del mejor, el mas simple."),
    }
