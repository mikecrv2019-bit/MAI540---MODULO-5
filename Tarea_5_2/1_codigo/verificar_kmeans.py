"""
Verifica por stdio (mismo protocolo que el MCP Inspector) la tool segmentar_kmeans.
Guarda el resultado en Tarea_5_2/2_evidencia_inspector/verificacion_kmeans.log.

    python verificar_kmeans.py
"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Vive en Tarea_5_2/1_codigo; el servidor está en la raíz del repositorio.
AQUI = Path(__file__).resolve().parents[2]
LOG = AQUI / "Tarea_5_2" / "2_evidencia_inspector" / "verificacion_kmeans.log"
lineas: list[str] = []


def salida(texto: str):
    print(texto)
    lineas.append(texto)


async def main():
    params = StdioServerParameters(
        command=sys.executable, args=[str(AQUI / "mcp_server.py")], cwd=str(AQUI)
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()
            salida("List Tools: " + str([t.name for t in (await s.list_tools()).tools]))

            for nombre, k in [("wine", 3), ("iris", 3)]:
                r = await s.call_tool("segmentar_kmeans", {"nombre": nombre, "k": k})
                d = json.loads(r.content[0].text)
                n = len(d["etiquetas"])
                d["etiquetas"] = f"<{n} etiquetas; primeras 10: {d['etiquetas'][:10]}>"
                salida(f"\n=== segmentar_kmeans({nombre!r}, k={k}) isError={r.is_error} ===")
                salida(json.dumps(d, indent=2, ensure_ascii=False))

            salida("\n##### Casos de error #####")
            for nombre, k in [("wine", 1), ("wine", 178), ("no_existe", 3), ("../pca_utils", 3)]:
                r = await s.call_tool("segmentar_kmeans", {"nombre": nombre, "k": k})
                salida(f"segmentar_kmeans({nombre!r}, k={k}) isError={r.is_error}")

    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text("\n".join(lineas), encoding="utf-8")


asyncio.run(main())
