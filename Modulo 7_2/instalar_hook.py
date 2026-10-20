"""Instala el hook de Git (pre-commit) que ejecuta las pruebas antes de cada commit.

Uso:  python instalar_hook.py      (primero hay que haber ejecutado:  git init)
"""
import os
import shutil
import stat
import sys

ORIGEN = os.path.join("hooks", "pre-commit")                # el script que viene con el proyecto
DESTINO = os.path.join(".git", "hooks", "pre-commit")       # donde Git lo busca

if not os.path.isdir(".git"):                               # sin repositorio no hay dónde instalar
    sys.exit("No encuentro la carpeta .git. Ejecuta primero:  git init")
shutil.copyfile(ORIGEN, DESTINO)                            # copia el script al lugar de Git
os.chmod(DESTINO, os.stat(DESTINO).st_mode | stat.S_IEXEC)  # lo vuelve ejecutable (en Mac y Linux)
print("Hook instalado: ahora las pruebas se ejecutan antes de cada commit.")
