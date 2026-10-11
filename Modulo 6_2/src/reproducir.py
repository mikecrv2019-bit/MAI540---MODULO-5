"""Reproduce todo el flujo de la Tarea 6.2 desde cero y guarda la salida de cada etapa.

Uso:  python src/reproducir.py
Etapa 1: busqueda_comparacion.py -> evidencia/salida_busqueda_comparacion.txt
Etapa 2: curvas_auditoria.py     -> evidencia/salida_curvas_auditoria.txt
Las cifras son deterministas (semillas fijas); solo los tiempos de ajuste varian con el equipo.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASOS = [
    ("Etapa 1 · busqueda y comparacion", RAIZ / "src" / "busqueda_comparacion.py", RAIZ / "evidencia" / "salida_busqueda_comparacion.txt"),
    ("Etapa 2 · curvas y auditoria", RAIZ / "src" / "curvas_auditoria.py", RAIZ / "evidencia" / "salida_curvas_auditoria.txt"),
]

for titulo, script, salida in PASOS:
    t0 = time.perf_counter()
    r = subprocess.run([sys.executable, str(script)], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        sys.exit(f"Fallo en {script.name}")
    salida.write_text(r.stdout, encoding="utf-8")
    print(f"{titulo}: ok en {time.perf_counter() - t0:.0f} s -> {salida.relative_to(RAIZ)}")
print("Listo.")
