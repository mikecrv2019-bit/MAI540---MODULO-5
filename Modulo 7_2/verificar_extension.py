"""Comprueba la estructura de la extensión (plugin) sin necesitar Claude Code.

Uso:  python verificar_extension.py            (revisa la carpeta extension)
      python verificar_extension.py otra_carpeta
"""
import glob
import json
import os
import re
import sys


def campos(ruta):
    """Lee el encabezado entre --- de un archivo .md y lo devuelve como diccionario (o None si no hay)."""
    texto = open(ruta, encoding="utf-8").read().replace("\r\n", "\n")
    m = re.match(r"^---\n(.*?)\n---\n", texto, re.S)
    if not m:
        return None
    pares = (linea.split(":", 1) for linea in m.group(1).split("\n") if ":" in linea)
    return {k.strip(): v.strip() for k, v in pares}


def revisar(carpeta):
    problemas, ok = [], []
    manifiesto = os.path.join(carpeta, ".claude-plugin", "plugin.json")
    if not os.path.isfile(manifiesto):
        return [], [f"falta {manifiesto}"]
    try:
        datos = json.load(open(manifiesto, encoding="utf-8"))
    except ValueError as error:                                     # JSON mal escrito
        return [], [f"plugin.json no es un JSON válido ({error})"]
    nombre = str(datos.get("name", ""))
    if not nombre or " " in nombre:
        problemas.append("plugin.json: `name` debe existir y no llevar espacios (usa guiones)")
    else:
        ok.append(f"manifiesto: {nombre}")
    if not datos.get("description"):
        problemas.append("plugin.json: falta `description`")
    comandos = sorted(glob.glob(os.path.join(carpeta, "commands", "*.md")))
    if not comandos:
        problemas.append("commands/: no hay ningún comando (.md)")
    for ruta in comandos:
        c = campos(ruta)
        if not c or not c.get("description"):
            problemas.append(f"{os.path.relpath(ruta, carpeta)}: falta `description` en el encabezado")
        else:
            ok.append(f"comando: /{nombre}:{os.path.basename(ruta)[:-3]}")
    for ruta in sorted(glob.glob(os.path.join(carpeta, "agents", "*.md"))):
        c = campos(ruta) or {}
        faltan = [k for k in ("name", "description", "tools") if not c.get(k)]
        if faltan:
            problemas.append(f"{os.path.relpath(ruta, carpeta)}: faltan {', '.join(faltan)} en el encabezado")
        else:
            ok.append(f"agente: {c['name']}")
    return ok, problemas


if __name__ == "__main__":
    carpeta = sys.argv[1] if len(sys.argv) > 1 else "extension"
    if not os.path.isdir(carpeta):
        sys.exit(f"No encuentro la carpeta '{carpeta}'. Créala como indica el instructivo.")
    ok, problemas = revisar(carpeta)
    for linea in ok:
        print("OK  ", linea)
    for linea in problemas:
        print("FALTA", linea)
    if problemas:
        sys.exit(1)
    print("La extensión tiene una estructura válida.")
