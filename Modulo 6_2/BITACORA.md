# Bitácora de desarrollo asistido · Tarea 6.2

Registro de mis instrucciones, lo que se verificó y las correcciones. Fecha de trabajo: 2026-10-10.
Asistente: Claude (Sonnet 5.5) en Claude Code. Todas las cifras de esta bitácora salen de `evidencia/` o de la salida de los comandos citados.

## 1. Instrucciones recibidas

1. «Actúa como un experto en machine learning y desarrolla la tarea 6.2 del Máster de IA, siguiendo las instrucciones que te adjunto **sin omitir nada**. Tampoco debes alucinar o inventar soluciones; si tienes dudas debes consultar antes de continuar.» Se adjuntó `credit_g.csv` y los 6 puntos de la tarea.
2. Tras preguntarme el asistente por sus dudas (la primera consulta se interrumpió y el usuario pidió que las enumerara en texto), respondí:
   - **Ubicación:** crear una carpeta `Modulo 6_2` en el repositorio `MAI540---MODULO-5`.
   - **Curva de aprendizaje de la 6.1:** opción A (reconstruirla con los modelos de la 6.1 y declararlo).
   - **Métrica de la búsqueda:** opción A (exactitud, registrando también el recall de «bad»).
   - **Skill de auditoría:** v2.0.
3. Pregunta pendiente que **no** respondí: el nombre del autor en la portada. Se dejó `German Credit 6.2` (mismo criterio que la 6.1); **confirmar**.

## 2. Contexto leído antes de escribir código

- Enunciado oficial `TAREA_6_2_….docx` (extraído del XML; coincide con el texto pegado y agrega los entregables: repositorio con commits atómicos, bitácora e informe APA de 3 páginas).
- Repositorio de la Tarea 6.1 (`MODULO 6/Tarea_6_1`): código, `metricas.md`, reporte del auditor y bitácora. Cifras base: árbol .698 y Random Forest .759 de exactitud en validación cruzada.
- Proyecto de clase `Demo_Credito_incompleto` (cuadrícula de ejemplo y estructura), y las dos versiones de la Skill del Módulo 4 (v1.4 y v2.0).
- Hallazgos que obligaron a consultar: (a) **el repositorio de la 6.1 no tiene curva de aprendizaje**, aunque el enunciado de la 6.2 la da por hecha; (b) hay dos versiones de la Skill; (c) el enunciado no da matriz de costos.

## 3. Decisiones que tomé yo (no consultadas; revisarlas)

| Decisión | Motivo |
|---|---|
| Excluir `age` y `personal_status` de las predictoras; `housing` sí es predictora y también se audita | El punto 5 dice «las variables sensibles se usan para auditar, no para decidir». Interpreté sensibles = edad y estado civil/sexo (atributos protegidos). Es un interruptor de una línea (`VARIABLES_SENSIBLES` en `src/datos.py`). Sensibilidad medida: con las 20 variables, HGB .758 (recall .483) frente a .766 (.510) con 18. |
| Cuadrícula `max_depth` × `min_samples_leaf` = 40 combinaciones (la del Demo de clase) | El enunciado pide «al menos dos» e indica estos dos como ejemplo. |
| Random Forest e HGB con parámetros por defecto | El punto 1 pide afinar el árbol; así su medición no tiene sesgo de selección. |
| CV interna de la búsqueda con semilla 43; externa 42 (igual que la 6.1) | Reproducir las cifras de la 6.1 y no usar la misma partición dentro y fuera. |
| Elegir **HistGradientBoosting** | Exactitud equivalente a Random Forest (.766 vs .765) y recall de «bad» más alto (.510 vs .417). Decisión tomada después de ver `busqueda_comparacion.md`. |
| Umbral de pytest para la desviación = 0.05 | ≈ 1.5 × √(.70·.30/200) = .032 (error estándar muestral de un pliegue de 200 casos). |
| Grupos de edad `<25`, `25-34`, `35-44`, `>=45` | Corte propio; otros cortes podrían cambiar V4. |
| No usar la matriz de costos 5:1 de UCI | Opción A elegida; el enunciado no la da. |
| Auditoría ejecutada por el mismo asistente que escribió el código | No pedí subagentes. La Skill se invocó y se siguió al pie de la letra, pero **no es una revisión independiente**. |

## 4. Qué verifiqué

- **Control de reproducción:** con las 20 variables y parámetros por defecto, el protocolo da árbol .6980 y Random Forest .7590, idénticos a la 6.1 (`salida_busqueda_comparacion.txt`, líneas 5-6).
- **Determinismo:** se corrió `src/reproducir.py` varias veces; las cifras no cambian, solo los tiempos de ajuste.
- **Consistencia con la matriz de confusión:** exactitud y recall de los cuatro modelos coinciden con los derivados de la matriz agregada (la prueba `test_evidencia_consistente_con_la_matriz` y V1.2 de la auditoría).
- **Pruebas:** 9 pruebas de pytest, todas pasan. La prueba de regresión `test_pipelines_no_comparten_estimador` se comprobó **fallando** al quitar temporalmente el `clone` de `src/modelos.py` y pasando al restaurarlo.
- **Auditoría:** `auditorias/AUDIT_REPORT_german_credit_6_2.md` (Skill v2.0): V1 PASA, V2 FALLA (V2.4), V3 FALLA (V3.1), V4 FALLA (V4.2), V5 NO SE PUEDE DETERMINAR (V5.1), V6 PASA. Las acciones recomendadas **no se aplicaron**, para que el informe corresponda exactamente al código commiteado y auditado.
- **Informe:** exportado a PDF con Word para contar páginas: portada + 3 páginas (incluye referencias). Todas las cifras del informe se leen de los JSON y del informe de auditoría.

## 5. Errores y correcciones

1. **Estimador compartido (error mío, detectado con una verificación de cordura).** En la primera corrida de las curvas, el árbol *por defecto* de la 6.1 mostraba exactitud de entrenamiento 0.785; un árbol sin límite debe dar ≈ 1.0. Causa: `crear_pipeline` reutilizaba el mismo objeto estimador y fijar los parámetros ganadores en el árbol afinado contaminó el árbol por defecto. Corrección: `clone(estimador)` dentro del Pipeline (`src/modelos.py`) y prueba de regresión. Tras la corrección: entrenamiento 1.000, validación .698 (coincide con la validación cruzada de la 6.1). Las cifras de la etapa 1 no cambiaron (ahí cada pipeline se creaba con objetos nuevos).
2. **Métrica de «más datos» ruidosa.** Mi primera medida (validación a 800 menos validación a 480 casos) dependía de un solo punto que es un valle. La reemplacé por la pendiente de una recta ajustada a la segunda mitad de la curva (+0.95 pp por 100 casos en HGB).
3. **Dato mal escrito en una prueba:** esperaba 11 categóricas en `X`; son 12 (13 menos `personal_status`). Corregido antes de commitear.
4. **Leyenda de la figura** tapaba datos; movida. Para el informe se dibujó una figura de tamaño nativo (6.4 × 1.85 in) desde `curvas.json`, porque al reducir la de evidencia sus fuentes quedaban ilegibles. Está en `informe/generar_informe.py`, fuera del código auditado.
5. **Informe de 5 páginas → 4:** recortes de texto y ajuste de figura; ningún elemento exigido se eliminó.
6. **Fallos de comandos de shell** por comillas anidadas (no afectaron resultados); los parches se hicieron con scripts en archivo.

## 6. Discrepancias conocidas que NO corregí

- `README.md` (líneas 68-71) trae tiempos de una corrida anterior (0.015, 0.197, 0.264 s) que difieren de la corrida final (`salida_busqueda_comparacion.txt` líneas 31-34: 0.016, 0.180, 0.263 s). Los tiempos no son deterministas; el informe usa los de `busqueda_comparacion.json`. La auditoría lo declara en sus limitaciones.
- `README.md` dice que el enunciado «establece que» aprobar un malo «cuesta más»; el enunciado dice que «suele costar más». El informe usa la redacción fiel. Dejé el README tal cual porque la auditoría cita ese fragmento literal.

## 7. Commits (reales; `git log`)

| Hash | Hora | Mensaje |
|---|---|---|
| a1d04da | 22:37:05 | chore(6.2): estructura, datos y dependencias de la Tarea 6.2 |
| cde5187 | 22:37:05 | feat(6.2): Skill de auditoria-modelos v2.0 (Modulo 4) en .claude/skills |
| 8374123 | 22:37:06 | feat(6.2): datos, Pipeline y protocolo de validacion unico |
| 31360e2 | 22:37:06 | feat(6.2): GridSearchCV del arbol, validacion anidada y comparacion de tres modelos |
| d679e3c | 22:37:06 | feat(6.2): curvas de aprendizaje, auditoria por subgrupo e interpretabilidad |
| 4aa6d8e | 22:37:07 | test(6.2): 9 pruebas pytest (…) |
| 2e797fd | 22:37:07 | docs(6.2): evidencia generada (JSON, Markdown, salidas) y curvas de aprendizaje |
| 557f081 | 22:37:07 | docs(6.2): README, descripcion de variables y declaracion del costo de errores |
| eeeebb1 | 22:40:30 | audit(6.2): informe de la Skill auditoria-modelos v2.0 sobre el modelo elegido |

Los commits agrupan el estado final de cada pieza; las horas no reflejan el orden real de trabajo (el código se escribió, corrió y corrigió antes de commitear; ver sección 5). Los commits del informe y de esta bitácora siguen en `git log`.

## 8. Pendientes

- **Push a GitHub:** no realizado (no se pidió publicar). Remoto: `mikecrv2019-bit/MAI540---MODULO-5`.
- **Autor de la portada:** confirmar «German Credit 6.2».
- **Acciones de la auditoría sin aplicar:** V2.4 (curvas sobre el mismo `X`), V3.1 (curva optimista del árbol afinado; conjunto reservado para elegir entre modelos), V4.2 (revisar `male div/sep` y `for free`), V5.1 (validar ausentes). Aplicarlas exigiría una nueva auditoría.
- **Texto del informe:** la recomendación y la lectura de la curva las redactó el asistente a partir de la evidencia; el estudiante debe revisarlas y hacerlas suyas.
- No se midió cuántos tokens o minutos consumió el desarrollo asistido.
