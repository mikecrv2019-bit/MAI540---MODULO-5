"""
Verificación por línea de comandos de las 5 piezas de mcp_server.py.

Usa el mismo protocolo (JSON-RPC sobre stdio) que el MCP Inspector, así que
cada llamada de aquí es equivalente a pulsar "Run Tool" / "Read Resource" /
"Get Prompt" en el Inspector. Guarda el resultado en evidencia/verificacion.log.

    python verificar_servidor.py
"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

AQUI = Path(__file__).parent
LOG = AQUI / "evidencia" / "verificacion.log"
lineas: list[str] = []


def salida(texto: str = ""):
    print(texto)
    lineas.append(texto)


def bloque(titulo: str, contenido):
    salida(f"\n=== {titulo} ===")
    if not isinstance(contenido, str):
        contenido = json.dumps(contenido, indent=2, ensure_ascii=False)
    salida(contenido)


async def main():
    params = StdioServerParameters(
        command=sys.executable, args=[str(AQUI / "mcp_server.py")], cwd=str(AQUI)
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()

            # --- Descubrimiento (pestañas Tools / Resources / Prompts) ---
            tools = (await s.list_tools()).tools
            bloque("List Tools", [t.name for t in tools])
            recursos = (await s.list_resources()).resources
            bloque("List Resources", [str(r.uri) for r in recursos])
            plantillas = (await s.list_resource_templates()).resource_templates
            bloque("List Resource Templates", [t.uri_template for t in plantillas])
            prompts = (await s.list_prompts()).prompts
            bloque("List Prompts", [p.name for p in prompts])

            # --- Tool 1 ---
            r = await s.call_tool("cargar_dataset", {"nombre": "iris"})
            bloque("[1/5] TOOL cargar_dataset(nombre='iris')  isError=%s" % r.is_error,
                   r.content[0].text)

            # --- Tool 2 ---
            r = await s.call_tool("ejecutar_pca", {"nombre": "iris", "n_componentes": 2})
            bloque("[2/5] TOOL ejecutar_pca(nombre='iris', n_componentes=2)  isError=%s" % r.is_error,
                   r.content[0].text)

            # --- Resource estático ---
            r = await s.read_resource("data://datasets")
            bloque("[3/5] RESOURCE data://datasets  mime=%s" % r.contents[0].mime_type,
                   r.contents[0].text)

            # --- Resource con plantilla ---
            r = await s.read_resource("data://datasets/wine")
            bloque("[4/5] RESOURCE data://datasets/wine  mime=%s" % r.contents[0].mime_type,
                   r.contents[0].text)

            # --- Prompt ---
            r = await s.get_prompt("interpretar_componentes",
                                   {"nombre": "iris", "n_componentes": "2"})
            bloque("[5/5] PROMPT interpretar_componentes(nombre='iris', n_componentes=2)",
                   "\n".join(f"[{m.role}] {m.content.text}" for m in r.messages))

            # --- Casos de error: el servidor debe rechazar, no filtrar nada ---
            salida("\n\n##### Casos de error / límites de permisos #####")
            for etiqueta, nombre in [
                ("tool con dataset inexistente", "no_existe"),
                ("tool con path traversal", "../pca_utils"),
            ]:
                r = await s.call_tool("cargar_dataset", {"nombre": nombre})
                bloque(f"{etiqueta} ({nombre!r})  isError={r.is_error}", r.content[0].text)
            r = await s.call_tool("ejecutar_pca", {"nombre": "iris", "n_componentes": 9})
            bloque("ejecutar_pca n_componentes=9 (iris solo tiene 4)  isError=%s" % r.is_error,
                   r.content[0].text)
            try:
                r = await s.read_resource("data://datasets/../pca_utils")
                bloque("resource con traversal", r.contents[0].text)
            except Exception as e:  # noqa: BLE001
                bloque("resource data://datasets/../pca_utils", f"rechazado: {e}")

    LOG.parent.mkdir(exist_ok=True)
    LOG.write_text("\n".join(lineas), encoding="utf-8")


asyncio.run(main())
