# Paso 5 · La extensión, archivo por archivo

La salida de `python verificar_extension.py` está en `04_verificar_extension.txt` (tres líneas OK y ninguna FALTA).
Qué haría cada archivo al cargar la carpeta con `claude --plugin-dir extension`:

| Archivo | Qué pasa al cargarse |
|---|---|
| `extension/.claude-plugin/plugin.json` | Claude Code reconoce la carpeta como plugin. Su `name` (`auditoria-equidad`, sin espacios) se vuelve el prefijo de sus comandos. |
| `extension/commands/vivienda.md` | Aparece el comando `/auditoria-equidad:vivienda`. Antes de que Claude responda, la línea `` !`python tareas.py vivienda` `` ejecuta la auditoría y le pasa la tabla; `allowed-tools` limita lo que puede ejecutar a ese único comando. Claude responde con una ficha de cuatro encabezados (hallazgo, evidencia, fiabilidad, siguiente comprobación) y no modifica archivos. |
| `extension/agents/auditor-de-equidad.md` | Aparece un agente que Claude puede invocar cuando alguien afirma que el modelo es mejor o peor para un grupo. Solo puede leer (`Read, Grep, Glob`): contrasta la afirmación con `datos.py`, `predictor.py` y `tareas.py` y devuelve una tabla Afirmación / ¿La sostienen los datos? / Qué falta. |

Prueba en vivo (opcional): desde la raíz del proyecto, `claude --plugin-dir extension`; luego
`/auditoria-equidad:vivienda` y, por ejemplo, «Usa el agente auditor-de-equidad para revisar esta afirmación: el
modelo acierta igual con todos los tipos de vivienda». Una captura de esa sesión se agrega como `05_claude_code.png`.
