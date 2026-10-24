# Bitácora final de desarrollo asistido — Capstone Dilitio Wine Corp (Tarea 8.2)

Registro de cómo se construyó y se verificó la herramienta con asistencia de Claude Code (modelo Sonnet 5.5), con corte al 2026-10-23.
Todas las cifras salen de `evidencia/` o de la salida de los comandos citados. Lo que solo el estudiante puede aportar o confirmar
está marcado **[confirmar]** o **[pendiente]** y se lista en la sección 10: esta bitácora no inventa lo que el estudiante hizo o dijo.

## 1. El problema que abordé

Dilitio Wine Corp quiere decidir de forma objetiva a qué línea de producto va cada lote de vino, y hoy no hay datos de cómo se decide.
La propuesta del Módulo 5.2 mostró con K-Means que la química separa tres perfiles. El capstone lo convierte en una herramienta
supervisada: dadas 13 mediciones de laboratorio, **¿a qué perfil químico (el cultivar) se parece el lote y con cuánta confianza?**
Apoya la decisión de una persona; no la toma. Datos: UCI Wine, 178 lotes, CC BY 4.0. Detalle en el `README.md`.

## 2. Estrategia de instrucciones con el asistente

La estrategia se fue afinando por tarea; lo que sigue está registrado en las bitácoras anteriores y en esta sesión.

| Tarea | Cómo instruí al asistente | Qué aprendí |
|---|---|---|
| 6.1 | Roles (analista, ingeniero de modelos, auditor) como subagentes independientes, con archivos de rol y límites. | Un rol se desvió (propuso escalar y logaritmos no pedidos); el orquestador lo descartó. Los límites explícitos importan. |
| 6.2 | «Actúa como un experto en machine learning […] siguiendo las instrucciones que te adjunto **sin omitir nada**. Tampoco debes alucinar o inventar soluciones; si tienes dudas debes consultar antes de continuar.» | El asistente consultó lo ambiguo (ubicación, métrica, versión de la Skill) y yo decidí. |
| 8.1 | Pegué el enunciado de seis puntos y pedí la convención de carpetas del curso (`Modulo 8_1`). | Las decisiones que dependían de mí quedaron marcadas **[decidir]**. |
| **8.2** | Pegué el enunciado completo (7 puntos), adjunté `ejemplo_despliegue/` y `ejemplo_degradacion/` como referencia, y fijé límites: **«no subas nada a GitHub aún»** y **«no hagas commit ni push»**. A mitad de la sesión interrumpí para preguntar qué faltaba; el asistente respondió con una lista de hecho / pendiente / solo mío, y yo di la orden de continuar. | Pedir un estado a mitad de camino evita que el asistente avance sobre supuestos; los límites sobre acciones externas (push) se respetaron. |

Principios que se repiten: el asistente lee antes de escribir, las acciones que salen del equipo (push, envío) requieren mi orden, y
lo que no se puede probar con datos se declara como pendiente o supuesto.

## 3. Decisiones que tomó la herramienta (y su razón)

| Decisión | Razón | Qué debo revisar |
|---|---|---|
| Despliegue = app local con **Gradio** (más línea de comandos), no Colab ni video | La guía pide «la opción más simple»; un Colab exigiría subir `src/`, el modelo y los datos, y su enlace muere al cerrar la celda. | **[decidir]** El enlace de Moodle: Gradio local no tiene enlace público (ver sección 10). |
| La pantalla tiene dos pestañas: un lote, y un archivo con control de deriva | Un lote responde «¿a qué se parece?»; el archivo es la única forma de vigilar el cambio del mundo. | — |
| Análisis de errores con los **178 lotes** en validación cruzada (cada lote lo predice un modelo que no lo vio), no con los 36 de la prueba final | Con 36 lotes, un error mueve el recall de una clase 7 a 10 puntos; con 178 hay 48 a 71 casos por clase. Las tablas usan una repetición para que cada lote cuente una vez. | El análisis no elige nada; solo describe. Pero por eso el umbral de confianza usó también los lotes de la prueba (hallazgo V3.1). |
| Grupos: clase real, terciles de `alcohol`, `proline` y `magnesium`, y banda de confianza; intervalos de Wilson | No hay edad, sexo ni estado civil. Prolina y magnesio dependen del método de laboratorio; alcohol es la variable que más separa. Wilson funciona con n pequeño. | **[decidir]** Los terciles son un corte propio; otros cortes podrían mover los conteos. |
| Detección de deriva: prueba KS por variable con corrección de Bonferroni, más % de lotes fuera de rango (alerta sobre 30 %) | Dos señales complementarias (la simulación mostró que cada una ve lo que la otra no). El 30 % es el doble del ~15 % de lotes que salen de rango sin cambio alguno. | El 30 % no se calibró con datos de la empresa. |
| Simulación: regresión logística, sesgo de prolina (+10, +25, +50 %), prolina y magnesio +25 %, ruido de 0.5 y 1.0 desviaciones; 100 repartos | Imita un cambio de método de medición y un instrumento ruidoso, sin cambiar una línea del modelo (como en `ejemplo_degradacion`). | **Son supuestos, no mediciones.** |
| Aviso de confianza baja bajo 80 % | En los 178 lotes, 12 caen bajo 0.80 y contienen los 3 errores (la confianza máxima de un error es 0.677). | Fijado mirando esos mismos errores, incluidos lotes de la prueba final: la auditoría lo marcó FALLA (V3.1). |
| Regla de reentrenar: exactitud con lotes nuevos < 0.931 (caída de 0.05) | Con 45 lotes de evaluación la exactitud varía unos 0.02; 0.05 son más de dos desviaciones. | Los «40 lotes» y «6 meses» son criterio propio, sin base empírica. |
| Informe en `.docx` APA 7, presentación en `.pptx`, bitácora en `.md` y `.docx` | Moodle pide archivos. | — |

**Origen del código al abrir la sesión de cierre.** Al comenzar esta sesión ya existían `app_gradio.py`, `src/interfaz.py`, `src/deriva.py`,
`src/detalle_errores.py`, `src/simular_degradacion.py` y sus pruebas (archivos fechados 2026-10-23, 12:31 a 12:43), sin commitear.
Esta sesión los leyó, los ejecutó y los verificó, pero no los escribió. **[confirmar]** Quién los escribió y con qué instrucciones.

## 4. Lo que verifiqué y con qué

| Qué | Cómo | Resultado |
|---|---|---|
| El código nuevo funciona | `pytest -v` completo | 40 pruebas en verde, 0 omitidas (`evidencia/pytest_v_final.txt`) |
| La app abre y se usa | Lancé `python app_gradio.py` y la abrí en el navegador integrado; botón «Lote ambiguo (el 83)» + «Clasificar lote» | `class_1`, 66 % de confianza y aviso «Confianza baja (< 80 %)». Servidor detenido después. |
| Lo que dice el README que se verá | Ejecuté las mismas funciones que usa la pantalla (`evaluar_archivo('datos/wine.csv')`, `evaluar_lote`) | 178 lotes, 4 con confianza baja, exactitud 100 % (lotes de entrenamiento), sin deriva; lote típico `class_0` 100 %. Coincide. |
| Las cifras no dependen del entorno | Reentrené con `python src/entrenar.py` y comparé `resultados.md` antes y después con `diff` | Idéntico. Desaparecieron los avisos de versión de scikit-learn. |
| La simulación es reproducible | Volví a correr `python src/simular_degradacion.py` | Mismas cifras (40 s). |
| El conjunto de datos y su licencia | Consulté la página de UCI y el registro DataCite | CC BY 4.0; año de cita 1992. |
| Las fuentes del informe existen | Crossref y arXiv para cada DOI (Gama 2014, Mitchell 2019, Kapoor y Narayanan 2023, Wilson 1927, Massey 1951, Abid 2019, Rabanser 2019) | Título, autores, revista, volumen y páginas coinciden. |
| Verificación independiente del modelo y su evaluación | Skill `auditoria-modelos` v2.0 sobre `src/` y `evidencia/` (`auditorias/AUDIT_REPORT_8_2.md`) | V2, V5 y V6 PASAN; V3 FALLA (V3.1); V1 y V4 NO SE PUEDE DETERMINAR (V1.5 sin costos; V4.2 con menos de 20 casos por clase). |

Lo que **no** verifiqué: una instalación limpia (clon nuevo y entorno nuevo) con el README de 8.2; `mcp dev` con el Inspector; el uso por una persona
distinta del autor (`revision/prueba_usuario.md`); la app con un navegador distinto o con otro sistema operativo.

## 5. Errores que encontré

| Error | Cómo apareció | Corrección |
|---|---|---|
| `requirements.txt` no incluía `gradio` | Al intentar abrir la app: `ModuleNotFoundError`. Una prueba de la pantalla se **omitía en silencio** por lo mismo (`1 skipped`). | Se agregó `gradio>=5.0` y `scipy>=1.11`; ahora 40 pruebas y 0 omitidas. |
| Una prueba omitida da falsa tranquilidad | Misma causa: el resumen de pytest decía «39 passed, 1 skipped». | Se instaló la dependencia; **[pendiente]** decidir si esa prueba debe fallar en vez de omitirse. |
| El modelo guardado venía de otra versión de scikit-learn (1.9.1 vs 1.9.0) | Avisos `InconsistentVersionWarning` al predecir. | Reentrenado en este entorno; resultados idénticos. (`modelos/` no se versiona: un clon limpio entrena el suyo.) |
| El README de 8.1 citaba el conjunto Wine como «1991» | Consulta a DataCite y a la página de UCI: año de cita 1992 (donación 1991). | Corregido en el README de 8.2; el de 8.1 no se tocó. |
| El README de 8.2 decía que la simulación tarda «1 o 2 minutos» | La medí: 40 s. | Corregido a «menos de un minuto». |
| La auditoría marcó **V3.1 FALLA**: el umbral de 80 % se fijó con los 178 lotes, que incluyen los 36 de la prueba final | Skill de auditoría. Ninguna cifra reportada depende del umbral, pero su captura de errores es optimista. | Declarado en README y `LIMITACIONES.md`. **No** se rehízo el umbral con solo el entrenamiento: queda como acción recomendada. |
| La leyenda tapaba una barra de la figura de degradación y el eje truncado no estaba rotulado | Revisión visual de la figura. | Leyenda sobre el gráfico y eje rotulado «eje desde 80». |
| Un reemplazo de texto dejó una línea mal sangrada en `figuras_informe.py` | `IndentationError` al regenerar. | Corregido y regenerado. |
| `README` afirmaba comportamientos de la pantalla sin haberlos comprobado | Me los releí antes de entregar. | Se comprobaron (sección 4) antes de dejarlos. |

## 6. Correcciones humanas, y por qué

Registradas en las bitácoras anteriores o en esta conversación (no se han inventado otras):

| Corrección | Por qué |
|---|---|
| Convención de carpetas `Modulo 8_1`, `Modulo 8_2` en el repositorio de módulos | Es como entrego el curso. |
| Corregí el autor de la portada del informe de la Tarea 6.2: `German Credit 6_2` (con guion bajo) | El asistente había dejado `German Credit 6.2` por una pregunta que yo no respondí (bitácora 6.2). |
| «No subas nada a GitHub aún» / «No hagas commit ni push» | Quiero revisar los entregables antes de que salgan de mi equipo. |
| Interrumpí la auditoría para pedir el estado de lo que faltaba | Evitar que el asistente siguiera sin saber qué pedía la tarea completa. |

**[pendiente]** Añadir aquí lo que yo haya corregido o decidido en 8.2 que no conste arriba (por ejemplo, si cambié el texto de una limitación o
descarté una opción de despliegue). La rúbrica pide correcciones humanas con su porqué; esta tabla solo incluye las que puedo respaldar.

## 7. Pruebas ejecutadas y resultado

`pytest -v`: **40 pruebas, 40 en verde, 20.78 s** (salida completa: `evidencia/pytest_v_final.txt`).

| Archivo | Pruebas | Qué comprueban |
|---|---|---|
| `test_datos.py` | 2 | Forma de los datos; se rechazan NaN y columnas faltantes. |
| `test_validacion.py` | 4 | Partición estratificada y sin traslape; escalador sin fuga; CV determinista de 15 estimaciones; `cv` que no cubre las filas falla con mensaje. |
| `test_seleccion.py` | 4 | El criterio elige el más simple entre equivalentes, no uno fuera de la desviación, descarta los que no superan la línea base; error claro con un modelo desconocido. |
| `test_modelo.py` | 4 | El modelo supera la línea base; su desviación es ≤ 0.05; la prueba final lo confirma; la elección no depende de la prueba. |
| `test_errores_segmentacion.py` | 2 | Análisis por categoría contra un caso calculado a mano; criterios del K-Means. |
| `test_detalle_errores.py` | 5 | Intervalo de Wilson contra un valor conocido; cada lote se predice una vez; confianza válida; los grupos cubren los 178 lotes; cada error tiene su explicación. |
| `test_deriva.py` | 6 | Sin cambio no hay alerta; un sesgo de prolina se detecta y se nombra; pocos lotes solo miran el rango; conteo fuera de rango; la simulación es reproducible; más ruido baja la exactitud. |
| `test_interfaz.py` | 8 | Lote típico y ambiguo; campo vacío; valor fuera de rango; archivo inválido; archivo completo; archivo con prolina desplazada; la pantalla Gradio se construye con sus 13 campos. |
| `test_predecir.py` | 5 | Lote válido; entradas inválidas; advertencia de rango; servidor MCP y su mensaje de error. |

Además: la prueba manual de la app (sección 4) y la auditoría de la Skill.

## 8. Resultado final y limitaciones conocidas

- **Modelo:** regresión logística. Validación cruzada 5×3: exactitud y F1 macro **0.981 ± 0.022** frente a 0.401 / 0.191 de la línea base; prueba final 35 de 36 (0.972).
- **Errores por categoría:** 3 errores en 178 lotes (2 de `class_1`, 1 de `class_2`); los 3 con confianza menor a 0.68. De los 12 lotes con confianza menor a 0.80, 3 fallan (25 %, IC 95 % de 9 a 53 %); con confianza de 0.80 o más, 0 errores en 166 lotes.
- **Degradación simulada:** con ruido de una desviación la exactitud cae de 0.983 a 0.871 y el modelo sigue devolviendo probabilidades; ninguna alerta sola alcanza (la de distribución ve el cambio de método; la de rango ve el ruido).
- **Limitaciones principales** (detalle en `LIMITACIONES.md`): predice el `cultivar` de un archivo público, no la línea de producto; 178 lotes de una sola fuente; ninguna prueba con datos reales de la empresa; el umbral de confianza se fijó con los mismos datos que describe; el uso por una persona distinta del autor está sin registrar.

## 9. Reflexión

Una página como máximo, en `REFLEXION.md`.

## 10. Pendiente del estudiante

- **[pendiente]** Prueba de uso con una persona distinta de usted (`revision/prueba_usuario.md`, sección 2) y el cambio que haga a partir de lo que le cueste. Es el 20 % de la nota.
- **[pendiente]** Revisión humana de los cambios (la guía pide una revisión documentada por una persona, el docente o la Skill) y abrir los pull requests de 8.1 y de esta rama cuando decida subir.
- **[pendiente]** El enlace de la demostración para Moodle: Gradio local no tiene enlace público; elegir entre enlazar el repositorio una vez subido, publicar un Colab o grabar un video.
- **[confirmar]** Quién escribió el código existente al abrir esta sesión (sección 3) y cualquier corrección suya de 8.2 (sección 6).
- **[confirmar]** Que `REFLEXION.md` describe cómo trabajó usted de verdad; es un borrador armado con la evidencia del repositorio.
- **[pendiente]** Instalación limpia con el README de 8.2 y decisión sobre la prueba omitida cuando falta una dependencia.
- **[pendiente]** Presentar ante el grupo en la modalidad que indique el docente.
- No se ha hecho **ningún commit ni push** de la Tarea 8.2.
