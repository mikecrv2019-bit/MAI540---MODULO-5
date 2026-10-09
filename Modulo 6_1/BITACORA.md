# Bitácora de ejecución · Tarea 6.1

Registro cronológico de cómo se ejecutó el flujo, incluyendo errores, correcciones y decisiones.
Fecha: 2026-10-09. Orquestador: Claude (Sonnet 5.5) en Claude Code. Los tres roles corrieron como subagentes
independientes (cada uno con contexto propio). Las horas de commit son las reales de `git log`, salvo la
salvedad indicada en la sección 6.

## 1. Lectura del encargo
- Se recibió el texto de los 5 puntos y la ruta de `credit_g.csv`.
- Se localizó y leyó el enunciado oficial `TAREA_6_1_….docx` (extracción del XML) y se verificó que coincide con el
  texto pegado. El .docx añade tres entregables que el texto pegado no mencionaba: repositorio con **≥5 commits
  atómicos**, evidencia por rol e **informe APA de 2 a 3 páginas**.
- También se leyeron la guía de entorno y el proyecto `Demo_Credito_incompleto` (esqueleto con TODO, solo para
  contexto; no se usó su código).
- Entorno verificado: Python 3.14.7, scikit-learn 1.9.0, pandas 2.3.3, numpy 2.5.3, python-docx y matplotlib presentes.
- CSV verificado: 1,000 filas, 21 columnas (20 variables + `clase`).
- Tropiezo menor: el primer script de lectura del .docx falló por codificación de consola (cp1252). Se reescribió
  con salida UTF-8. Sin efecto en los resultados.

## 2. Preguntas al usuario (el usuario pidió preguntar ante dudas)
| Pregunta | Respuesta |
|---|---|
| ¿Subagentes reales o secuencial por el orquestador? | Subagentes reales |
| ¿Dónde crear el proyecto? | `MODULO 6/Tarea_6_1` (repo git propio) |
| ¿Autor de la portada APA? | «German Credit 6.1» (escrito por el usuario) |

## 3. Preparación del repositorio
- Carpeta `Tarea_6_1` creada con `git init`, copia de `credit_g.csv`, `requirements.txt`, `README.md`, `.gitignore`.
- **Incidente de identidad git:** el repo nuevo no tenía usuario configurado y git tomó uno automático
  (`jaime lopez <…@atlantisuniversity.edu>`). Se comparó con el repo de MODULO 5 (usa `mikecrv2019`) y se configuró esa
  identidad localmente; se reescribieron **solo los 2 commits locales recién creados** (`rebase --root --reset-author`).
  Nada estaba publicado.
- Los tres archivos de rol (`.claude/agents/*.md`) los redactó el orquestador: responsabilidad, qué puede/no puede
  tocar y entregable de cada uno.

## 4. Ejecución de los roles

### Rol 1 · Analista de datos (subagente)
- Duración 70 s · 90,448 tokens · 10 usos de herramientas.
- Entregó: `src/datos.py`, `src/analisis_datos.py`, `evidencia/01_analista_datos/resumen_datos.{md,json}`.
- Hallazgos: 1000×20 (13 categóricas, 7 numéricas); 700 good / 300 bad; línea base «siempre bueno» = .700; sin
  faltantes ni duplicados; `purpose=retraining` tiene 9 filas; «none» es categoría válida, no faltante.
- Revisión del orquestador: se leyó el resumen y el cargador; se ejecutó `python src/datos.py` (confirmó 1000×20,
  300 bad, 13 categóricas).
- **Desvío detectado por el orquestador:** el resumen recomendaba escalar, aplicar logaritmos y reportar F1/AUC, algo
  fuera de lo que pide la tarea. Se **descartó** en las instrucciones al Rol 2 (única transformación: codificación
  dentro del Pipeline; métricas pedidas: exactitud y recall de bad).
- Commit `b175d27`.

### Rol 2 · Ingeniero de modelos (subagente)
- Duración 161 s · 96,147 tokens · 12 usos de herramientas.
- Recibió: su archivo de rol, el resumen del analista y las precisiones del orquestador (recall por pliegue, 30
  semillas 0..29 además del subconjunto 0..9, `OrdinalEncoder` con `unknown_value=-1`, sin búsqueda de hiperparámetros).
- Entregó: `src/modelos.py`, `validacion.py`, `particion_unica.py`, `ejecutar_ingeniero.py`,
  `evidencia/02_ingeniero_modelos/metricas.{md,json}`.
- Dificultad que reportó: un primer intento de crear archivos con heredoc de bash falló por comillas y no creó nada; los
  reescribió con la herramienta Write.
- Revisión del orquestador: se leyó el código (Pipeline con `prep` + `modelo`, `StratifiedKFold(5, True, 42)`,
  `stratify=y` en la partición) y las tablas.
- Commit `f7cf3a9`.

### Rol 3 · Auditor (subagente)
- Duración 178 s · 131,487 tokens · 18 usos de herramientas.
- Se le pidió ser independiente y escéptico, recalcular sin importar `validacion.py`/`particion_unica.py` e inspeccionar
  los Pipeline reales. No se le indicó ningún hallazgo esperado.
- Entregó `evidencia/03_auditor/verificar.py` y `verificacion_salida.txt`. Veredicto: **aprobado con observaciones**,
  55/55 verificaciones OK, sin fuga de información. Ningún error de cálculo.
- **Bloqueo de herramienta:** su intento de escribir `reporte_auditor.md` fue rechazado («Subagents should return findings
  as text, not write report files»). El auditor no lo eludió y devolvió el contenido como texto.
- **Qué hizo el orquestador (y qué NO se resolvió):** el bloqueo no se levantó ni se eludió; sigue vigente para los
  subagentes. El orquestador, en su propia sesión, transcribió el mensaje del auditor a `reporte_auditor.md`
  con una nota de procedencia al inicio del archivo. Esto debilita la separación de funciones: el archivo lo escribió
  un rol distinto al auditor, aunque su contenido es el del auditor.
- Verificación del orquestador: se volvió a ejecutar `verificar.py` (salida idéntica a la guardada, 55/55).
- Commit `4856c96`.

## 5. Cierre
- `src/reproducir.py` ejecuta los tres roles en orden. Corrida desde cero: **49 s**, y `git status` quedó sin cambios
  (cifras reproducidas). Commit `448bf72`.
- Informe: `informe/generar_informe.py` lee todas las cifras de `metricas.json` y genera el .docx APA 7. Se exportó a PDF con
  Word para contar páginas: portada + 3 páginas.
- **Correcciones al borrador del informe antes de cerrar:**
  1. El borrador decía que `reproducir.py` regenera todo «en segundos»; al medirlo fueron 49 s. Se corrigió a «unos 50
     segundos en este equipo».
  2. El borrador decía que la prueba de `retraining` «demuestra que no hay fuga»; se suavizó a «muestra que el
     codificador se ajusta solo con los datos de entrenamiento».
- Commits `0fd523b` (informe) y `4d0458f` (README).

## 6. Commits (reales; `git log`)
| Hash | Hora | Mensaje |
|---|---|---|
| 54da63d | 12:24:06* | chore: estructura del proyecto, datos y dependencias |
| 3eecddb | 12:24:06* | feat(roles): define analista de datos, ingeniero de modelos y auditor |
| b175d27 | 12:25:47 | feat(analista): cargador de datos y resumen de German Credit |
| f7cf3a9 | 12:28:43 | feat(ingeniero): pipeline, validación cruzada y partición única |
| 4856c96 | 12:32:38 | feat(auditor): verificación independiente y reporte |
| 448bf72 | 12:32:38 | feat: script para reproducir el flujo completo desde cero |
| 0fd523b | 12:36:46 | docs(informe): informe técnico APA 7 |
| 4d0458f | 12:36:47 | docs: resultados y entregables en el README |

\* Los dos primeros commits muestran la misma hora porque la reescritura de autor (sección 3) reinició su fecha; no es
la hora en que se crearon. Los commits 4856c96/448bf72 comparten hora porque se hicieron en una sola orden.

## 7. Costo total medido
Subagentes: 90,448 + 96,147 + 131,487 = **318,082 tokens**; 70 + 161 + 178 = **409 s (≈ 6.8 min)**. No incluye los
tokens ni el tiempo del orquestador. No se midió la alternativa de hacerlo todo en una sola conversación.

## 8. Pendientes que no se hicieron
- **Push a GitHub:** no realizado (no se dispone de la URL del repositorio ni se pidió publicar).
- **Autor de la portada:** quedó «German Credit 6.1» tal como se indicó; confirmar si es el dato correcto.
- Texto de la evaluación crítica (punto 5): redactado por el orquestador a partir de lo ocurrido; el estudiante debe revisarlo.
