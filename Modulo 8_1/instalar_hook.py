"""Instala el hook de Git (pre-commit) que ejecuta las pruebas antes de cada commit.

Uso (desde cualquier carpeta del repositorio):  python Modulo 8_1/instalar_hook.py
"""
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

ORIGEN = Path(__file__).resolve().parent / "hooks" / "pre-commit"   # el script que viene con el proyecto

try:
    destino = subprocess.run(["git", "rev-parse", "--git-path", "hooks/pre-commit"], capture_output=True,
                             text=True, check=True, cwd=ORIGEN.parent).stdout.strip()
except (subprocess.CalledProcessError, FileNotFoundError):
    sys.exit("No encuentro un repositorio Git. Ejecuta primero:  git init  (o clona el repositorio)")

destino = Path(destino) if os.path.isabs(destino) else (ORIGEN.parent / destino).resolve()
shutil.copyfile(ORIGEN, destino)                              # copia el script al lugar donde Git lo busca
os.chmod(destino, os.stat(destino).st_mode | stat.S_IEXEC)    # lo vuelve ejecutable (Mac y Linux)
print(f"Hook instalado en {destino}: las pruebas se ejecutan antes de cada commit.")
