# Bitácora de desarrollo asistido — Tarea 8.1 (capstone Dilitio Wine Corp)

Registro de la sesión del 2026-10-22 con Claude Code (modelo Sonnet 5.5). Las decisiones de las que debe responder el
estudiante están marcadas con **[decidir]**; lo que solo el estudiante puede aportar, con **[pendiente]**.

## 1. Instrucción recibida

El enunciado de la Tarea 8.1 (seis puntos): herramienta completa con CV y línea base; ramas y PR con revisión; al menos cinco
pruebas con `pytest -v` guardado; Skill de auditoría aplicada; README con la plantilla y prueba con un tercero; historial limpio.

## 2. Decisiones de la herramienta (Claude) y su razón

| Decisión | Razón | Revisar |
|---|---|---|
| Proyecto = Dilitio Wine Corp (propuesta `5_2/4_documentos/`) | Es la única propuesta de capstone en el repositorio; los Módulos 6 y 7 usan German Credit. | **[decidir]** Si el capstone acordado con el docente es otro, esto no sirve. |
| Problema supervisado: predecir `cultivar` desde la química | La propuesta usaba K-Means (sin validación cruzada ni línea base posibles); el enunciado exige ambas. `cultivar` es el único dato etiquetado. | **[decidir]** `cultivar` no es la línea de producto de la empresa; está dicho en las Limitaciones del README. |
| Prueba final del 20 % + CV 5×3 sobre el 80 % | Con 178 filas, 3 repeticiones estabilizan la media; la prueba se mide una sola vez. | — |
| Criterio de selección: F1 macro, superar la base por 0.10 y elegir el más simple dentro de una desviación del mejor | Escrito antes de ver la prueba final; sin costos de la empresa, F1 macro trata las clases por igual. | **[decidir]** El umbral 0.10 y la regla de una desviación son convenciones elegidas aquí. |
| Hiperparámetros fijos, sin búsqueda | Evita necesitar validación anidada con tan pocos datos; todos los modelos tienen la misma oportunidad. | — |
| Dos ramas: `feat/modelo-validado` y `feat/herramienta-readme` | Una por funcionalidad (modelado / uso y documentación). | — |
| Revisor del PR = Skill de auditoría + revisión de Claude | La Skill está permitida como revisor por el enunciado; Claude no es una persona. | **[pendiente]** Revisión humana (docente o compañero), a anotar en `revision/`. |
| Carpeta `Modulo 8_1/` en el repositorio `MAI540---MODULO-5` (como `Modulo 5_1`, `Modulo 6_2`, `Modulo 7_2`) | Es la convención de nombres que pidió el estudiante para entregar. La carpeta se llamó antes `Capstone_Dilitio_Wine`; se renombró también en la historia local (antes de subir nada) para que los commits muestren la ruta final. | — |
| Hook `pre-commit` en `hooks/` (pytest + búsqueda de claves) | Es el patrón del Módulo 7; solo actúa si el commit toca `Modulo 8_1/`. | — |

## 3. Lo que se verificó (y cómo)

- Cada commit pasó por el hook: `evidencia/hook_commit_aceptado.txt` (commit aceptado con 16 pruebas) y
  `hook_commit_cancelado.txt` (commit cancelado por una prueba que falla a propósito, que no se conservó).
- Auditoría 1 (`auditorias/AUDIT_REPORT_1_antes_de_PR.md`): V2.1 y V3.1 fallan, V1.5 y V4.2 no se pueden determinar.
  Auditoría 2 (`AUDIT_REPORT_2_final.md`), hecha desde cero tras las correcciones: V2.1 y V3.1 pasan; quedan V1.5 y V4.2 sin determinar.
- Clon limpio con entorno nuevo siguiendo el README: mismas cifras con pandas 3.1.0 en lugar de 2.3.3 (`revision/prueba_instalacion.md`).
- Servidor MCP probado por stdio con el mismo protocolo del Inspector (`evidencia/verificacion_servidor.log`).
- `mcp dev` con el Inspector en el navegador **no se probó** en esta sesión.

## 4. Errores encontrados y correcciones

| Error | Cómo apareció | Corrección |
|---|---|---|
| El hook se cancelaba a sí mismo | El patrón de claves del propio `hooks/pre-commit` coincidía con la búsqueda. | Se excluye `hooks/` de la búsqueda. |
| Escalador de K-Means ajustado con las 178 filas (`segmentacion.py:28`) | Skill, V2.1 y V3.1. | `segmentar` usa solo el entrenamiento; la silueta subió a 0.2875 y ya no necesita tolerancia. |
| `evaluar_cv` aceptaba un `cv` que dejaba filas sin predicción fuera de pliegue | Revisión de código del PR 1. | Error explícito y prueba (primer intento de la prueba no fallaba: con 3 pliegues sí cubre todo; se corrigió a 10 pliegues). |
| `requirements.txt` sin `mcp[cli]` | Instalación limpia. | Corregido. |
| La tool MCP devolvía solo «Error executing tool» | Log de `verificar_servidor.py`. | Devuelve el motivo. |
| `python -m venv` falla con rutas largas en Windows | Instalación limpia (WinError 267). | Nota en el README. |
| Un comando de varias líneas con comillas falló sin ejecutar nada | Herramienta de shell. | Los archivos se escribieron con la herramienta de escritura; no dejó rastro en el repositorio. |

## 5. Resultado

Regresión logística elegida: F1 macro CV 0.981 ± 0.022 frente a 0.191 ± 0.004 de la línea base; prueba final 35/36 (0.972).
21 pruebas en verde (`evidencia/pytest_v_final.txt`). Es un conjunto fácil: la cifra no prueba que sirva con vinos de la empresa.

## 6. Pendiente del estudiante

- **[pendiente]** Persona externa que instale con el README (`revision/prueba_instalacion.md`, sección 2).
- **[pendiente]** Revisión humana del PR y respuesta a sus comentarios.
- **[pendiente]** Abrir los pull requests en GitHub (el navegador integrado no tiene permiso para github.com) y pegar el texto de `revision/PR1_*.md` y `PR2_*.md`.
- **[pendiente]** Reflexión personal sobre cómo evolucionó su criterio técnico (la pide la Tarea 8.2, no esta).
