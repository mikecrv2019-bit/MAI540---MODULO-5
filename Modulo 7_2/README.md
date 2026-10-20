# Demo Clase 7 · Aplicación híbrida: un modelo predictivo y un modelo de lenguaje

Un Random Forest (el de la Clase 6) predice la probabilidad de que un crédito sea malo. Un modelo de lenguaje
pequeño redacta la explicación. Una capa de verificación comprueba que el texto no afirme nada que el modelo no
sustente, y si falla, se muestra un texto de respaldo armado solo con datos. Esta es la versión **incompleta**: los bloques `TODO` se escriben en clase.

## Instalación

Requiere Python 3.10 a 3.12 (en Mac con chip Intel, Python 3.12). Con el entorno virtual activo:

```bash
pip install -r requirements.txt
python probar_modelo.py      # comprueba que el modelo de lenguaje descarga y responde
```

## Qué hay en cada archivo

| Archivo | Qué hace |
|---|---|
| `datos.py` | Lee German Credit y traduce una solicitud a datos legibles |
| `predictor.py` | El modelo predictivo (Random Forest) y la probabilidad de crédito malo |
| `red_neuronal.py` | Una red neuronal sencilla: capas y pesos |
| `explicador.py` | El modelo de lenguaje que redacta la explicación |
| `verificador.py` | Las verificaciones y el texto de respaldo |
| `main.py` | Ejecuta la aplicación completa sobre N solicitudes (`python main.py 200`) y guarda los textos |
| `tareas.py` | Comandos reutilizables: `evaluar`, `auditar`, `probar` y `vivienda` (auditoría por tipo de vivienda) |
| `hooks/pre-commit` y `instalar_hook.py` | La automatización: pruebas antes de cada commit |
| `tests/test_hibrido.py` | Pruebas automáticas |
| `verificar.py` | Comprueba un bloque: `python verificar.py <número de TODO>` |
| `verificar_extension.py` | Comprueba la estructura de la extensión: `python verificar_extension.py` |

## Cómo se completa

Cada `TODO n` marca un bloque que se escribe en clase. Para verificar cada paso:

```bash
python verificar.py 1     # cambia el número para cada bloque
python main.py            # cuando estén todos los bloques
pytest -v                 # con los TODO 10 y 11
```
La versión terminada está en `Demo_Hibrido_completo/`.

## Tarea 7.1 · Automatización y extensión

- Comando propio: `python tareas.py vivienda` (exactitud y créditos malos detectados por tipo de vivienda).
- Hook: `python instalar_hook.py` instala `hooks/pre-commit` (pytest y búsqueda de TODO pendientes). Requiere `git init`.
- Extensión propia: `extension/` (`auditoria-equidad`), se comprueba con `python verificar_extension.py`.
- Evidencia en `evidencia/` e informe APA en `informe/` (`python informe/generar_informe.py` lo regenera).

## La extensión (plugin)

Un plugin es una carpeta que empaqueta comandos y agentes para reutilizarlos en otro proyecto. Se arma en el paso 23 del instructivo y se comprueba con `python verificar_extension.py`. Con Claude Code se carga con `claude --plugin-dir extension` y sus comandos aparecen como `/auditoria-hibrida:auditar` y `/auditoria-hibrida:probar`.

## Tarea 7.2 · Aplicación híbrida con verificación

- `python comparar_modelos.py`: red neuronal frente al Random Forest sobre las mismas 200 solicitudes de prueba.
- `python main.py 20` (o `200`): recorre N solicitudes; los textos quedan en `evidencia/textos_generados.json` y se reutilizan (`--regenerar` los vuelve a pedir al modelo).
- `verificador.py` suma dos reglas a `verificar_explicacion`: `verificar_datos` (el texto no contradice cuenta corriente ni vivienda, ni inventa atributos) y `verificar_tono_medio` (ni «alto» ni «bajo» con probabilidad de 30 % a 60 %). `verificar_base` conserva el verificador de clase para medir el antes.
- `python medir_efecto.py 200`: tabla de rechazos antes y después; usa `evidencia/etiquetas.json` (revisión manual) para contar falsos positivos.
- Pruebas: `pytest -v` (71: las 5 originales, `tests/test_regla_datos.py` y `tests/test_regla_tono_medio.py`).
- Informe APA: `python informe/generar_informe_7_2.py`. Bitácora: `bitacora/Bitacora_Tarea_7_2.md`.
- Agente nuevo en la extensión: `revisor-de-explicaciones`.
- Historial: los commits de la Tarea 7.2 se hicieron en un repositorio propio (donde el hook `pre-commit` corrió las pruebas en cada commit, y canceló uno mal ordenado) y se integraron aquí con su mensaje; el primero de esta carpeta es el punto de partida (el proyecto con la 7.1 terminada). Para las pruebas: crea un entorno virtual, instala las dependencias de `requirements.txt` (con Python 3.14 los pines de `transformers` y `numpy` no se instalan; se usaron versiones más nuevas) y ejecuta `pytest -v` dentro de `Modulo 7_2/`. Para regenerar los textos con el modelo de lenguaje: `python main.py 200 --regenerar`.
