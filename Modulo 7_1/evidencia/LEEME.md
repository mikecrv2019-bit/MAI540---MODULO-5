# Evidencia de la Tarea 7.1

| Captura | Texto | Paso | Qué muestra |
|---|---|---|---|
| `captura_1_commit_aceptado.png` | `terminal_1_commit_aceptado.txt` | 2 | Commit aceptado: el hook corre las pruebas (5 passed) |
| `captura_2_commit_cancelado.png` | `terminal_2_commit_cancelado.txt` | 2 | Commit cancelado: se cambió `0.30` por `0.99` en `verificar_tono` y una prueba falla |
| `captura_3_hook_ampliado_aceptado.png` | `terminal_3_hook_ampliado_aceptado.txt` | 3 | La segunda comprobación (sin TODO pendientes) corre y el commit pasa |
| `captura_4_hook_ampliado_cancelado.png` | `terminal_4_hook_ampliado_cancelado.txt` | 3 | La segunda comprobación cancela un commit que pytest dejaba pasar |

| Archivo | Paso | Qué muestra |
|---|---|---|
| `01_commit_aceptado.txt`, `02_commit_cancelado.txt`, `03_hook_ampliado.txt` | 2 y 3 | Salida literal de las terminales, con la explicación de cada caso |
| `04_verificar_extension.txt` | 4 | `python verificar_extension.py` sin ninguna línea FALTA |
| `05_extension_que_hace_cada_archivo.md` | 5 | Qué hace cada archivo de la extensión al cargarse |

Las capturas son de las terminales reales; los `.txt` son la misma salida en texto.
