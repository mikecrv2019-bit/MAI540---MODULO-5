"""Verifica por linea de comandos las dos tools de src/mcp_server.py (mismo protocolo que el MCP Inspector).

    python verificar_servidor.py        # guarda evidencia/verificacion_servidor.log
"""
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

AQUI = Path(__file__).resolve().parent
LOG = AQUI / "evidencia" / "verificacion_servidor.log"
lineas = []


def salida(titulo, contenido):
    texto = f"\n=== {titulo} ===\n" + (contenido if isinstance(contenido, str) else json.dumps(contenido, indent=2, ensure_ascii=False))
    print(texto)
    lineas.append(texto)


async def main():
    params = StdioServerParameters(command=sys.executable, args=[str(AQUI / "src" / "mcp_server.py")],
                                   cwd=str(AQUI / "src"))
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as s:
            await s.initialize()
            salida("List Tools", [t.name for t in (await s.list_tools()).tools])

            r = await s.call_tool("resumen_validacion", {})
            resumen = json.loads(r.content[0].text)
            salida(f"TOOL resumen_validacion  isError={r.is_error}", {
                "elegido": resumen["seleccion"]["elegido"],
                "f1_macro_cv": {n: round(v["f1_macro"]["media"], 3) for n, v in resumen["validacion_cruzada"].items()},
            })

            lote = {"alcohol": 14.23, "malic_acid": 1.71, "ash": 2.43, "alcalinity_of_ash": 15.6, "magnesium": 127.0,
                    "total_phenols": 2.8, "flavanoids": 3.06, "nonflavanoid_phenols": 0.28, "proanthocyanins": 2.29,
                    "color_intensity": 5.64, "hue": 1.04, "od280/od315_of_diluted_wines": 3.92, "proline": 1065.0}
            r = await s.call_tool("clasificar_lote", {"valores": lote})
            salida(f"TOOL clasificar_lote (lote 0)  isError={r.is_error}", r.content[0].text)

            r = await s.call_tool("clasificar_lote", {"valores": {**lote, "proline": 20000.0}})
            salida("TOOL clasificar_lote (prolina 20000, fuera de rango)", r.content[0].text)

            r = await s.call_tool("clasificar_lote", {"valores": {"alcohol": 14.0}})
            salida(f"TOOL clasificar_lote (lote incompleto)  isError={r.is_error}", r.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
    LOG.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print(f"\nGuardado en {LOG.relative_to(AQUI)}")
