# Paso 5 · La extensión, archivo por archivo

La salida de `python verificar_extension.py` está en `04_verificar_extension.txt` (tres líneas OK y ninguna FALTA).
Qué haría cada archivo al cargar la carpeta con `claude --plugin-dir extension`:

| Archivo | Qué pasa al cargarse |
|---|---|
| `extension/.claude-plugin/plugin.json` | Claude Code reconoce la carpeta como plugin. Su `name` (`auditoria-equidad`, sin espacios) se vuelve el prefijo de sus comandos. |
| `extension/commands/vivienda.md` | Aparece el comando `/auditoria-equidad:vivienda`. Antes de que Claude responda, la línea `` !`python tareas.py vivienda` `` ejecuta la auditoría y le pasa la tabla; `allowed-tools` limita lo que puede ejecutar a ese único comando. Claude responde con una ficha de cuatro encabezados (hallazgo, evidencia, fiabilidad, siguiente comprobación) y no modifica archivos. |
| `extension/agents/auditor-de-equidad.md` | Aparece un agente que Claude puede invocar cuando alguien afirma que el modelo es mejor o peor para un grupo. Solo puede leer (`Read, Grep, Glob`): contrasta la afirmación con `datos.py`, `predictor.py` y `tareas.py` y devuelve una tabla Afirmación / ¿La sostienen los datos? / Qué falta. |

## Prueba en vivo con Claude Code

Desde la raíz del proyecto: `claude --plugin-dir extension`.

- `05_claude_code_comando.png`: `/auditoria-equidad:vivienda` ejecutó `python tareas.py vivienda` y respondió con la ficha de
  cuatro encabezados (Hallazgo, Evidencia, Fiabilidad, Siguiente comprobación). Señala que `propia` solo detecta el 26 % de
  los créditos malos con la misma exactitud (0,77) que los otros grupos, y que `sin costo` es poco fiable (22 casos).
- `05_claude_code_agente.png`: se le pidió al agente `auditor-de-equidad` revisar «el modelo acierta igual con todos los
  tipos de vivienda, así que es justo con todos». Concluyó que la afirmación **no está sustentada**: leyó `tareas.py`,
  `datos.py` y `predictor.py`, comprobó que la vivienda es variable predictora y que no hay intervalos de confianza, y no
  modificó ningún archivo.
