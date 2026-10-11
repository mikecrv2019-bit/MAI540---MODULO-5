"""Reproduce el flujo completo en el orden de los roles: analista -> ingeniero -> auditor.

Uso:  python src/reproducir.py
Regenera las evidencias de evidencia/01_*, 02_* y la salida del auditor. Es determinista:
si el repositorio queda sin cambios (`git status`), los numeros del informe se reproducen.
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASOS = [
    ("Rol 1 · Analista de datos", RAIZ / "src" / "analisis_datos.py", None),
    ("Rol 2 · Ingeniero de modelos", RAIZ / "src" / "ejecutar_ingeniero.py", None),
    ("Rol 3 · Auditor", RAIZ / "evidencia" / "03_auditor" / "verificar.py",
     RAIZ / "evidencia" / "03_auditor" / "verificacion_salida.txt"),
]

for titulo, script, salida in PASOS:
    print(f"== {titulo}: {script.relative_to(RAIZ)}")
    r = subprocess.run([sys.executable, str(script)], cwd=RAIZ, capture_output=True,
                       text=True, encoding="utf-8", env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    if r.returncode != 0:
        print(r.stdout, r.stderr)
        sys.exit(f"Fallo en {script.name}")
    if salida is not None:
        salida.write_text(r.stdout, encoding="utf-8")
    ultimas = [l for l in r.stdout.strip().splitlines() if l.strip()][-1:]
    print("   ok" + (f" · {ultimas[0]}" if ultimas else ""))
print("Listo. Revisa `git status`: sin cambios = numeros reproducidos.")
