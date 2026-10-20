"""Tarea 7.2 · Punto 5: tabla de rechazos antes y después de las dos reglas nuevas, sobre los MISMOS textos.

Uso:  python medir_efecto.py [N]
Lee evidencia/textos_generados.json (lo escribe main.py) y compara el verificador de clase (verificar_base) con el
verificador ampliado (verificar_explicacion). Si existe evidencia/etiquetas.json (revisión manual por solicitud:
«correcto», «reserva» o «incorrecto»), calcula también falsos positivos y fallos que siguen sin atraparse.
"""
import json
import os
import sys
from collections import Counter

from verificador import verificar_base, verificar_explicacion

MOTIVOS = [                                   # (nombre en la tabla, parte del mensaje que lo identifica)
    ("número no sustentado", "número no sustentado"),
    ("tono incoherente (<30% o >60%)", "pero la probabilidad es"),
    ("afirmación absoluta", "afirmación absoluta"),
    ("contradice un dato (cuenta/vivienda)", "pero el dato es"),
    ("afirmación sin dato", "sin dato que la respalde"),
    ("tono incoherente (30% a 60%)", "está entre 30% y 60%"),
]


def motivos(problemas):
    """Conjunto de nombres de motivo presentes en una lista de problemas."""
    return {nombre for p in problemas for nombre, clave in MOTIVOS if clave in p}


def medir(registros, etiquetas=None):
    filas = []
    for r in registros:
        antes = verificar_base(r["texto"], r["datos"], r["prob"])
        despues = verificar_explicacion(r["texto"], r["datos"], r["prob"])
        filas.append({**r, "antes": antes, "despues": despues, "etiqueta": (etiquetas or {}).get(str(r["solicitud"]))})
    return filas


def tabla(filas, titulo):
    n = len(filas)
    ant, des = Counter(), Counter()
    for f in filas:
        ant.update(motivos(f["antes"]))
        des.update(motivos(f["despues"]))
    lineas = [f"### {titulo}", "", "| Motivo del rechazo | Antes | Después |", "|---|---:|---:|"]
    for nombre, _ in MOTIVOS:
        lineas.append(f"| {nombre} | {ant[nombre]} | {des[nombre]} |")
    ra, rd = sum(bool(f["antes"]) for f in filas), sum(bool(f["despues"]) for f in filas)
    lineas.append(f"| **Textos rechazados (cada texto cuenta una vez)** | **{ra} de {n}** | **{rd} de {n}** |")
    lineas.append(f"| Textos que se muestran tal como los redactó el modelo | {n - ra} | {n - rd} |")
    etiquetados = [f for f in filas if f["etiqueta"]]
    if len(etiquetados) == n:
        def cuenta(clave, rechazado, etiqueta):
            return sum((bool(f[clave]) == rechazado) and f["etiqueta"] == etiqueta for f in etiquetados)
        lineas.append(f"| Falsos positivos (rechazó un texto correcto) | {cuenta('antes', True, 'correcto')} | {cuenta('despues', True, 'correcto')} |")
        lineas.append(f"| Textos incorrectos que aun así pasaron | {cuenta('antes', False, 'incorrecto')} | {cuenta('despues', False, 'incorrecto')} |")
        lineas.append(f"| Textos con reservas (afirmación evaluativa sin dato) que pasaron | {cuenta('antes', False, 'reserva')} | {cuenta('despues', False, 'reserva')} |")
        lineas.append(f"| Textos correctos que se muestran | {cuenta('antes', False, 'correcto')} | {cuenta('despues', False, 'correcto')} |")
    return "\n".join(lineas)


if __name__ == "__main__":
    with open(os.path.join("evidencia", "textos_generados.json"), encoding="utf-8") as f:
        registros = json.load(f)
    ruta_etiquetas = os.path.join("evidencia", "etiquetas.json")
    etiquetas = json.load(open(ruta_etiquetas, encoding="utf-8")) if os.path.exists(ruta_etiquetas) else {}
    N = int(sys.argv[1]) if len(sys.argv) > 1 else len(registros)
    filas = medir(registros[:N], etiquetas)
    print(tabla(filas, f"Primeras {N} solicitudes de prueba"))
    print("\nTextos rechazados SOLO por las reglas nuevas:")
    for f in filas:
        if f["despues"] and not f["antes"]:
            print(f"  #{f['solicitud']} ({f['prob']:.0%}, etiqueta: {f['etiqueta'] or 'sin revisar'}): {'; '.join(f['despues'])}")
