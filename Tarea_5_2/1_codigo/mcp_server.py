"""
Servidor MCP: dos tools, dos resources, un prompt.

Este es el archivo que el profesor completa en vivo durante la Clase 5.1,
siguiendo el mismo patrón del curso de Anthropic "Introduction to Model
Context Protocol" (M02), adaptado de un chatbot de documentos a un
servidor de análisis de datos.

Tools    -> operaciones que Claude puede decidir ejecutar (cargar un dataset,
            correr PCA).
Resources -> datos que el cliente puede pedir directamente, sin pasar por
            una decisión de Claude (la lista de datasets, la ficha de uno).
Prompt   -> una plantilla ya evaluada para una tarea recurrente: interpretar
            componentes principales en términos del dominio, no solo en
            términos de varianza.

ESTADO: INCOMPLETO A PROPÓSITO.
Cada bloque "# TODO" de abajo es una pieza que se escribe en vivo durante la
clase, siguiendo el patrón de @mcp.tool / @mcp.resource / @mcp.prompt que ya
viste en las diapositivas 10, 11 y 12. La lógica de negocio (pca_utils.py) ya
está completa — aquí solo falta envolverla con el decorador correcto.

Para probar este archivo una vez completado, sin cliente ni CLI:
    mcp dev mcp_server.py
Abre el Inspector en el navegador, conecta, y prueba cada tool/resource/prompt
a mano antes de conectarlo a nada más.
"""

from mcp.server.mcpserver import MCPServer, UserMessage
from pydantic import Field

import kmeans_utils
import pca_utils

mcp = MCPServer("analisis-datos")


# ---------------------------------------------------------------------------
# Tools — algo que Claude DECIDE ejecutar, con los argumentos que el modelo
# elige según lo que pida quien está conversando.
# ---------------------------------------------------------------------------

@mcp.tool(
    name="cargar_dataset",
    description=(
        "Carga un dataset de la carpeta datasets/ y devuelve su forma (filas), "
        "sus columnas numéricas y sus columnas categóricas. Úsala SIEMPRE ANTES "
        "de ejecutar_pca, para saber qué columnas numéricas tiene el dataset y "
        "cuántos componentes máximos se pueden pedir."
    ),
)
def cargar_dataset(
    nombre: str = Field(description="Nombre del dataset sin extensión, p. ej. 'iris' o 'wine'"),
) -> dict:
    return pca_utils.describir_dataset(nombre)


@mcp.tool(
    name="ejecutar_pca",
    description=(
        "Ejecuta PCA (con estandarización previa) sobre las columnas numéricas "
        "de un dataset. Devuelve la varianza explicada por componente, la "
        "varianza acumulada y las cargas (loadings) de cada variable original "
        "en cada componente. Usa cargar_dataset antes para conocer las columnas."
    ),
)
def ejecutar_pca(
    nombre: str = Field(description="Nombre del dataset sin extensión, p. ej. 'iris' o 'wine'"),
    n_componentes: int = Field(
        description="Número de componentes principales a extraer (entre 1 y el número de columnas numéricas)"
    ),
) -> dict:
    return pca_utils.ejecutar_pca(nombre, n_componentes)


@mcp.tool(
    name="segmentar_kmeans",
    description=(
        "Segmenta un dataset con K-Means (con estandarización previa) sobre sus "
        "columnas numéricas. Devuelve la etiqueta de grupo de cada fila, el "
        "tamaño de cada grupo, la inercia y el coeficiente de silueta del k "
        "elegido. Usa cargar_dataset antes para conocer las columnas."
    ),
)
def segmentar_kmeans(
    nombre: str = Field(description="Nombre del dataset sin extensión, p. ej. 'iris' o 'wine'"),
    k: int = Field(description="Número de grupos (entero >= 2 y menor que el número de filas)"),
) -> dict:
    return kmeans_utils.ejecutar_kmeans(nombre, k)


# ---------------------------------------------------------------------------
# Resources — datos que el CLIENTE pide directamente, sin que Claude decida
# nada. Estático (siempre lo mismo) o con plantilla (un parámetro en la URI).
# ---------------------------------------------------------------------------

@mcp.resource("data://datasets", mime_type="application/json")
def listar_datasets() -> list[str]:
    return pca_utils.listar_datasets()


@mcp.resource("data://datasets/{nombre}", mime_type="application/json")
def ficha_dataset(nombre: str) -> dict:
    return pca_utils.describir_dataset(nombre)


# ---------------------------------------------------------------------------
# Prompt — una plantilla YA EVALUADA para una tarea que se repite, en vez de
# dejar que cada usuario improvise su propia pregunta de interpretación.
# ---------------------------------------------------------------------------

@mcp.prompt(
    name="interpretar_componentes",
    description=(
        "Plantilla para interpretar, en términos del dominio y no solo de "
        "varianza, los componentes principales de un dataset."
    ),
)
def interpretar_componentes(
    nombre: str = Field(description="Nombre del dataset sin extensión, p. ej. 'iris' o 'wine'"),
    n_componentes: int = Field(description="Número de componentes principales a interpretar"),
) -> list[UserMessage]:
    prompt = f"""
Ejecuta PCA sobre el dataset '{nombre}' con {n_componentes} componentes usando
la tool ejecutar_pca y, con el resultado, interpreta cada componente:

1. Identifica las 2-3 variables con mayor carga (en valor absoluto) en cada componente.
2. Explica qué patrón del dominio de '{nombre}' podría representar cada componente
   a partir de esas variables, no solo cuánta varianza captura.
3. Indica si el signo de las cargas tiene una lectura razonable (p. ej. variables
   que se oponen entre sí dentro del mismo componente).

Termina diciendo si {n_componentes} componentes alcanzan según la varianza
acumulada, o si convendría usar más o menos.
"""
    return [UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
