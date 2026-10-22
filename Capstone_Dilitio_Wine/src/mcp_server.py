"""Servidor MCP del capstone (continuacion del servidor del Modulo 5): dos tools sobre el modelo validado.

    mcp dev src/mcp_server.py        # Inspector en el navegador

Tools:  clasificar_lote (perfil quimico de un lote)  y  resumen_validacion (cifras de CV y criterio de seleccion).
Solo lee evidencia/resultados.json y modelos/modelo_final.joblib; no recibe rutas ni escribe archivos.
"""
import json

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from datos import RAIZ
from predecir import clasificar_lote as _clasificar_lote

mcp = MCPServer("capstone-dilitio-wine")


@mcp.tool(
    name="clasificar_lote",
    description=(
        "Clasifica un lote de vino en uno de los tres perfiles quimicos (class_0, class_1, class_2) a partir de sus "
        "13 variables: alcohol, malic_acid, ash, alcalinity_of_ash, magnesium, total_phenols, flavanoids, "
        "nonflavanoid_phenols, proanthocyanins, color_intensity, hue, od280/od315_of_diluted_wines, proline. "
        "Devuelve el perfil, las probabilidades y advertencias si algun valor sale del rango de entrenamiento."
    ),
)
def clasificar_lote(
    valores: dict[str, float] = Field(description="Diccionario con las 13 variables quimicas del lote"),
) -> dict:
    return _clasificar_lote(valores)


@mcp.tool(
    name="resumen_validacion",
    description=(
        "Devuelve la validacion cruzada (media y desviacion de exactitud y F1 macro) de la linea base y los modelos "
        "candidatos, el modelo elegido y la regla con que se eligio. Requiere haber corrido src/entrenar.py."
    ),
)
def resumen_validacion() -> dict:
    r = json.loads((RAIZ / "evidencia" / "resultados.json").read_text(encoding="utf-8"))
    return {
        "validacion_cruzada": {n: {"exactitud": v["exactitud"], "f1_macro": v["f1_macro"]}
                               for n, v in r["validacion_cruzada"].items()},
        "seleccion": r["seleccion"],
        "prueba_final": r["prueba_final"],
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
