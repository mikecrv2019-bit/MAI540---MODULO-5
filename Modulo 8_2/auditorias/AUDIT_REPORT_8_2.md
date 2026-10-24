# Informe de auditoría — Capstone Dilitio Wine Corp, Tarea 8.2 (despliegue, errores por categoría y degradación)

- **Archivos auditados:** `Modulo 8_2/src/datos.py`, `modelos.py`, `validacion.py`, `seleccion.py`, `errores.py`, `segmentacion.py`, `entrenar.py`, `predecir.py`, `detalle_errores.py`, `deriva.py`, `interfaz.py`, `simular_degradacion.py`; salidas guardadas `Modulo 8_2/evidencia/resultados.json`, `errores_detalle.json`, `degradacion.json`
- **Archivos de apoyo leídos:** `Modulo 8_2/README.md`
- **Columna objetivo:** `cultivar` — codificación: texto, `class_0`, `class_1`, `class_2` (evidencia: `datos.py:16` `CLASES = ["class_0", "class_1", "class_2"]`; `datos.py:43` `return df[PREDICTORAS].copy(), df[OBJETIVO].copy()`)
- **Tipo de problema:** clasificación multiclase, 3 clases (evidencia: `modelos.py:24` `LogisticRegression(max_iter=1000, random_state=SEMILLA)`)
- **Subgrupos:** `cultivar` (categorías de la propia variable objetivo) y terciles de `alcohol`, `proline` y `magnesium` (origen: argumento; `detalle_errores.py:25` `VARIABLES_GRUPO = ["alcohol", "proline", "magnesium"]`). El proyecto no tiene atributos protegidos (`detalle_errores.py:10`).
- **Skill:** auditoria-modelos v2.0 — fecha: 2026-10-23
- **Modificaciones al proyecto:** ninguna (auditoría de solo lectura; el código no se ejecutó dentro de la auditoría)

Desbalance (paso previo): `71/48 = 1.4792 < 1.5` con la distribución de `resultados.json:8-10` (`class_0` 59, `class_1` 71, `class_2` 48) → **sin desbalance** según la definición de la Skill.

## Resumen

| Verificación | Resultado |
|---|---|
| V1 Métricas reportadas | NO SE PUEDE DETERMINAR |
| V2 Partición de datos | PASA |
| V3 Fuga de información | FALLA |
| V4 Disparidad entre subgrupos | NO SE PUEDE DETERMINAR |
| V5 Validez de datos de entrada | PASA |
| V6 Variables no admisibles | PASA |

## Tabla de verificación

| ID | Verificación | Resultado | Evidencia | Observación |
|---|---|---|---|---|
| V1.1 | Rango válido | PASA | `resultados.json:272` `"exactitud": 0.9722222222222222`; `resultados.json:273` `"f1_macro": 0.9709618874773139` | Exactitudes, F1, recall y precisión guardados (`resultados.json`, `errores_detalle.json`) están en [0, 1]; ninguno es NaN. |
| V1.2 | Consistencia con la matriz | PASA | Matriz de prueba `resultados.json:335-351` (`[12,0,0],[0,14,0],[0,1,9]`) | Exactitud `(12+14+9)/36 = 0.9722` (reportada 0.9722). Precisión `class_1` `14/(14+1) = 0.9333` (reportada 0.9333). Recall `class_2` `9/10 = 0.9` (reportado 0.9). F1 macro `(1.0+0.9655+0.9474)/3 = 0.9710` (reportada 0.9710). Diferencias ≤ 0.001. |
| V1.3 | Clase positiva correcta | PASA | `errores.py:10` `cm = confusion_matrix(y_real, y_pred, labels=clases)`; `validacion.py:46` `f1_score(y.iloc[te], p, average="macro")` | Reporte por clase con etiqueta explícita; F1 macro no usa clase positiva. |
| V1.4 | No solo accuracy con desbalance | PASA | `71/48 = 1.4792 < 1.5`; `errores.py:15-17` `recall = verdaderos / reales ...` | Sin desbalance bastaría accuracy; además el código calcula F1 macro, recall, precisión, matriz y línea base (`entrenar.py:40-42`). |
| V1.5 | Métrica acorde al costo | NO SE PUEDE DETERMINAR | `README.md:16` `La empresa no entregó una matriz de costos y aquí no se supone ninguna` | Multiclase sin clase de interés ni costos distintos por tipo de error. El proyecto lo declara (F1 macro), pero la Skill exige un error más caro declarado para dar PASA. |
| V2.1 | División antes del preprocesamiento que aprende | PASA | `modelos.py:23` `("escalado", StandardScaler()),`; `validacion.py:43` `modelo = clone(estimador).fit(X.iloc[tr], y.iloc[tr])`; `segmentacion.py:31` `esc = StandardScaler().fit(X_tr)` | Clasificadores: el escalado va dentro del `Pipeline` y se ajusta por pliegue. K-Means: ajustado solo con `X_tr`. `simular_degradacion.py:62` ajusta con `X_ent`. `deriva.py` solo calcula mínimos, máximos y pruebas KS contra datos de referencia, sin `fit`. El ajuste final con los 178 lotes (`entrenar.py:62` `final = clone(modelos[elegido]).fit(X, y)`) ocurre después de reportar toda métrica y está declarado en el README. |
| V2.2 | Semilla fija | PASA | `validacion.py:20` `random_state=SEMILLA`; `validacion.py:24` `random_state=SEMILLA`; `simular_degradacion.py:61` `random_state=semilla`; `simular_degradacion.py:63` `rng = np.random.default_rng(1000 + semilla)`; `detalle_errores.py:41` `random_state=semilla` | Semilla entera en partición, CV, modelos aleatorios (`modelos.py:24,27,30,33`), K-Means (`segmentacion.py:20,35`) y simulación. Los generadores se crean dentro de la función o del bucle que los usa; no hay generador global. |
| V2.3 | Estratificación | PASA | `validacion.py:20` `stratify=y`; `validacion.py:24` `RepeatedStratifiedKFold(...)`; `simular_degradacion.py:61` `stratify=y` | Todas las particiones del proyecto están estratificadas. |
| V2.4 | Misma partición para los modelos comparados | PASA | `entrenar.py:28` `{nombre: evaluar_cv(est, X_tr, y_tr) for nombre, est in crear_modelos().items()}` | Mismo `X_tr`, `y_tr` y `crear_cv()` con semilla fija (`validacion.py:39`); el escalado diferente va dentro del `Pipeline`. |
| V3.1 | Nada se ajusta con datos de prueba | FALLA | `interfaz.py:12` `UMBRAL_CONFIANZA = 0.80   # en detalle_errores.py los 3 errores de 178 lotes tuvieron confianza < 0.68, y 12 lotes < 0.80`; `detalle_errores.py:140` `X, y = cargar_datos()` | El umbral de aviso de confianza baja se fijó mirando los errores de los 178 lotes, que incluyen los 36 de la prueba final. Elegir el modelo sí respeta la separación (`entrenar.py:36-37` usa solo CV del entrenamiento; la prueba se mide una vez, `entrenar.py:40`), y ninguna cifra reportada (0.981 de CV, 0.972 de prueba) depende de ese umbral. Pero la tasa de captura de errores que se atribuye al umbral (3 de 3) es optimista: el umbral se eligió con esos mismos errores. |
| V3.2 | Ninguna columna posterior a la predicción | PASA | `datos.py:4-5` `Ninguna de las 13 predictoras se calcula a partir de la etiqueta (son mediciones de laboratorio)`; lista literal en `datos.py:17-21` | Las 13 predictoras son mediciones tomadas al analizar el lote. Exactitud de prueba 0.9722 (`resultados.json:272`), no 1.0. |
| V4.1 | Métrica por subgrupo | PASA | `resultados.json:357-376` recall, precisión y F1 por `cultivar` en la prueba final; `errores_detalle.json:8-11,24-27,40-43` tasa de error por clase con 178 lotes; `errores_detalle.json:59-146` por terciles | La métrica se calcula por cada valor de `cultivar` y por tercil de las tres variables, y está guardada. |
| V4.2 | Disparidad dentro del umbral | NO SE PUEDE DETERMINAR | `resultados.json:359,365,371` `"n": 12`, `"n": 14`, `"n": 10` | No hay clase positiva y en la prueba ninguna clase llega a 20 casos. Complemento fuera del criterio (178 lotes fuera de pliegue): recall `class_0` 59/59 = 1.000, `class_1` 69/71 = 0.972, `class_2` 47/48 = 0.979 contra el global `175/178 = 0.983`; brecha máxima `0.983 − 0.972 = 0.011 ≤ 0.10`. Terciles: error máximo `2/59 = 0.034` contra `3/178 = 0.017`; diferencia 0.017 ≤ 0.10. Con 3 errores en total las diferencias entre grupos no son concluyentes. |
| V5.1 | Sin `inf`/`NaN` al entrenar | PASA | `datos.py:32` `if num.isna().any().any() or not np.isfinite(num.to_numpy(dtype=float)).all():`; `datos.py:42` `df = validar_datos(pd.read_csv(ruta))` | La validación se llama dentro de `cargar_datos`, que usan el entrenamiento, el análisis de errores y la simulación. No hay divisiones entre columnas. Archivos subidos a la pantalla se validan en `interfaz.py` (`leer_archivo`). |
| V6.1 | Sin identificadores ni atributos prohibidos | PASA | `datos.py:17-21` lista de 13 predictoras | Todas son mediciones químicas; ninguna es un identificador ni un atributo protegido. |

## Acciones recomendadas

1. **[V3.1]** (prioridad: alta, por ser FALLA) Fijar el umbral de confianza solo con los 142 lotes de entrenamiento y reportar cuántos errores de la prueba final (36 lotes) captura, o declarar explícitamente en el README y en `LIMITACIONES.md` que el umbral se fijó con los 178 lotes y que su capacidad real de captura es probablemente menor que la observada. (El README y `LIMITACIONES.md` ya dicen que se fijó mirando los 3 errores; falta decir que incluyen lotes de la prueba final.)
2. **[V1.5]** (prioridad: media) Obtener de la empresa qué error cuesta más (por ejemplo, enviar un lote premium a la línea de entrada); sin eso, la métrica queda como F1 macro por igualdad entre clases.
3. **[V4.2]** (prioridad: media) Conseguir más lotes etiquetados: con menos de 20 casos por clase en la prueba no se puede decidir la disparidad entre clases con el criterio de la Skill.

## Limitaciones de esta auditoría

- El código y las pruebas no se ejecutaron dentro de la auditoría (regla de solo lectura); los números provienen de las salidas guardadas en `evidencia/`.
- `interfaz.py`, `deriva.py` y `simular_degradacion.py` no entrenan el modelo elegido; se auditaron en lo que toca a ajuste de transformadores, semillas, particiones y umbrales.
- La Skill evalúa el modelo y su evaluación, no la calidad de la pantalla Gradio ni el uso por parte de una persona (ver `revision/prueba_usuario.md`).
