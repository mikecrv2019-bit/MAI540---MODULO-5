# Informe de auditoría — Capstone Dilitio Wine Corp (rama `feat/modelo-validado`, antes del PR 1)

- **Archivos auditados:** `Capstone_Dilitio_Wine/src/datos.py`, `modelos.py`, `validacion.py`, `seleccion.py`, `errores.py`, `segmentacion.py`, `entrenar.py`; salida guardada `Capstone_Dilitio_Wine/evidencia/resultados.json`
- **Archivos de apoyo leídos:** ninguno (la carpeta aún no tiene `README.md`, `context.md` ni `DESCRIPCION.md`; solo se usan las docstrings de `datos.py` y `seleccion.py` como declaración del autor)
- **Columna objetivo:** `cultivar` — codificación: texto, `class_0`, `class_1`, `class_2` (evidencia: `datos.py:16` `CLASES = ["class_0", "class_1", "class_2"]`; carga en `datos.py:43` `return df[PREDICTORAS].copy(), df[OBJETIVO].copy()`)
- **Tipo de problema:** clasificación multiclase, 3 clases (evidencia: `modelos.py:21` `DummyClassifier(strategy="most_frequent")`, `modelos.py:27` `DecisionTreeClassifier(max_depth=3, random_state=SEMILLA)`)
- **Subgrupos:** `cultivar` (origen: argumento). Observación: es la propia variable objetivo (categorías), no un atributo protegido; el proyecto no tiene atributos protegidos (datos químicos de lotes de vino).
- **Skill:** auditoria-modelos v2.0 — fecha: 2026-10-22
- **Modificaciones al proyecto:** ninguna (auditoría de solo lectura)

Desbalance (paso previo): `71/48 = 1.4792 < 1.5` con la distribución `resultados.json:8-10` (`"class_0": 59`, `"class_1": 71`, `"class_2": 48`) → **sin desbalance** según la definición de la Skill.

## Resumen

| Verificación | Resultado |
|---|---|
| V1 Métricas reportadas | NO SE PUEDE DETERMINAR |
| V2 Partición de datos | FALLA |
| V3 Fuga de información | FALLA |
| V4 Disparidad entre subgrupos | NO SE PUEDE DETERMINAR |
| V5 Validez de datos de entrada | PASA |
| V6 Variables no admisibles | PASA |

## Tabla de verificación

| ID | Verificación | Resultado | Evidencia | Observación |
|---|---|---|---|---|
| V1.1 | Rango válido | PASA | `resultados.json:64` `"media": 0.9812807881773398`; `resultados.json:272` `"exactitud": 0.9722222222222222` | Todas las exactitudes, F1, recall y precisión de `resultados.json` están en [0, 1] y ninguna es NaN. |
| V1.2 | Consistencia con la matriz | PASA | `resultados.json:335-351` matriz de prueba `[12,0,0],[0,14,0],[0,1,9]` y `:272` `"exactitud": 0.9722222222222222` | Exactitud: `(12+14+9)/36 = 0.9722` (reportada 0.9722). Precisión class_1: `14/(14+1) = 0.9333` (`:367`). Recall class_2: `9/10 = 0.9` (`:372`). F1 macro: `(1.0+0.9655+0.9474)/3 = 0.9710` (reportada 0.9710). Matriz fuera de pliegue (`:277-292`): recall class_1 `54/57 = 0.9474`, precisión class_0 `47/49 = 0.9592`; coinciden. Nota: la exactitud CV media (`:64`, 0.9813) es el promedio de 15 pliegues y no se deriva de la matriz fuera de pliegue (una repetición; `139/142 = 0.9789`); son magnitudes distintas, no una inconsistencia. |
| V1.3 | Clase positiva correcta | PASA | `errores.py:10` `cm = confusion_matrix(y_real, y_pred, labels=clases)` | Reporte por clase con etiqueta explícita (`errores.py:12-18`); F1 macro sin clase positiva (`validacion.py:46` `f1_score(y.iloc[te], p, average="macro")`). |
| V1.4 | No solo accuracy con desbalance | PASA | `71/48 = 1.4792 < 1.5` (`resultados.json:8-10`) | Sin desbalance reportar accuracy bastaría; además el código calcula F1 macro, recall y precisión por clase, matriz y línea base (`entrenar.py:40-42`). |
| V1.5 | Métrica acorde al costo | NO SE PUEDE DETERMINAR | `seleccion.py:3` `Metrica de decision: F1 macro de la validacion cruzada` | Multiclase: el proyecto no identifica una clase de interés ni declara costos distintos por tipo de error (no hay `README.md`/`DESCRIPCION.md` con esa declaración). |
| V2.1 | División antes del preprocesamiento que aprende | FALLA | `segmentacion.py:28` `Xe = StandardScaler().fit_transform(X)` | El escalador del K-Means se ajusta con todo `X` (incluye las filas de la prueba final). Las rutas supervisadas pasan: el escalado va dentro del `Pipeline` (`modelos.py:23` `("escalado", StandardScaler())`) y se ajusta por pliegue (`validacion.py:43` `modelo = clone(estimador).fit(X.iloc[tr], y.iloc[tr])`). |
| V2.2 | Semilla fija | PASA | `validacion.py:20` `random_state=SEMILLA`; `validacion.py:24` `random_state=SEMILLA`; `segmentacion.py:31` `rng = np.random.default_rng(SEMILLA)` | Semilla entera en partición, CV, árbol/RF/boosting (`modelos.py:24,27,30,33`) y KMeans (`segmentacion.py:19`). `DummyClassifier(most_frequent)` es determinista. El generador se crea dentro de `segmentar`. |
| V2.3 | Estratificación | PASA | `validacion.py:20` `stratify=y`; `validacion.py:24` `RepeatedStratifiedKFold(...)` | Clasificación: ambas particiones estratificadas. |
| V2.4 | Misma partición para los modelos comparados | PASA | `entrenar.py:28` `{nombre: evaluar_cv(est, X_tr, y_tr) for nombre, est in crear_modelos().items()}` | Todos reciben el mismo `X_tr`, `y_tr` y `crear_cv()` con semilla fija (`validacion.py:39`); el preprocesamiento diferente va dentro del `Pipeline`. |
| V3.1 | Nada se ajusta con datos de prueba | FALLA | `segmentacion.py:28` `Xe = StandardScaler().fit_transform(X)`; `entrenar.py:55` `"segmentacion_kmeans": segmentar(X, y)` | `segmentar` recibe todo `X` (178 filas), no `X_tr`. Alcance: el K-Means es exploratorio y no interviene en la elección del clasificador. La elección sí pasa: usa solo CV del entrenamiento (`entrenar.py:36` `cv = comparar_modelos(X_tr, y_tr)`, `:37` `decision = elegir_modelo(cv)`), no se afinan hiperparámetros (valores fijos en `modelos.py`) y la prueba se mide una vez (`entrenar.py:40`). El ajuste final con los 178 lotes (`entrenar.py:62`) ocurre después de reportar y no genera ninguna métrica. |
| V3.2 | Ninguna columna posterior a la predicción | PASA | `datos.py:5` `13 predictoras se calcula a partir de la etiqueta (son mediciones de laboratorio)`; `datos.py:43` `df[PREDICTORAS].copy()` | Lista literal de 13 mediciones químicas (`datos.py:17-21`), ninguna construida con `cultivar`; se conocen al analizar el lote. Exactitud de prueba 0.9722 (`resultados.json:272`), no 1.0. |
| V4.1 | Métrica por subgrupo | PASA | `errores.py:11-18` `por_clase[clase] = {"n": reales, "recall": recall, ...}`; `resultados.json:357-376` | Recall, precisión y F1 por cada valor de `cultivar` sobre la prueba final. |
| V4.2 | Disparidad dentro del umbral | NO SE PUEDE DETERMINAR | `resultados.json:359,365,371` `"n": 12`, `"n": 14`, `"n": 10` | Ninguna clase tiene ≥ 20 casos en la prueba (class_0 = 12, class_1 = 14, class_2 = 10). Evidencia complementaria fuera del criterio: en la predicción fuera de pliegue (n = 47, 57, 38) los recall son 1.000, 0.947 y 1.000 contra una exactitud de `139/142 = 0.9789`: diferencias máximas `0.9789 - 0.9474 = 0.0315 ≤ 0.10`. |
| V5.1 | Sin `inf`/`NaN` al entrenar | PASA | `datos.py:32` `if num.isna().any().any() or not np.isfinite(...)`; `datos.py:42` `df = validar_datos(pd.read_csv(ruta))` | No hay divisiones ni `errors="coerce"`; la validación se ejecuta en el flujo real (`entrenar.py:32` `X, y = cargar_datos()`). |
| V6.1 | Sin identificadores ni atributos prohibidos | PASA | `datos.py:17-21` lista `PREDICTORAS` | Ninguna predictora es un identificador (`alcohol`, `proline`, `flavanoids`, …) ni un atributo prohibido; `resultados.json:4` `"predictoras": 13`. |

## Acciones recomendadas

1. **[V2.1]** Ajustar el escalador y el K-Means solo con el entrenamiento (`segmentar(X_tr, ...)`) y medir los grupos de la prueba con `predict`; si se mantiene una réplica del piloto sobre las 178 filas, declararla aparte como descriptiva y sin decisión asociada (prioridad: alta).
2. **[V3.1]** Misma corrección que V2.1: `entrenar.py:55` debe llamar a `segmentar` con la partición de entrenamiento (prioridad: alta).
3. **[V1.5]** Declarar en el `README.md` qué errores cuestan más para Dilitio Wine Corp (por ejemplo, enviar un lote a una línea que no le corresponde) o, si no hay costos, escribir explícitamente que se tratan por igual y por qué se usa F1 macro (prioridad: media).
4. **[V4.2]** Documentar que con 36 filas de prueba ninguna clase llega a 20 casos y reportar la comparación por clase con las predicciones fuera de pliegue (n ≥ 38) como evidencia complementaria; no hay forma de alcanzar n ≥ 20 por clase en la prueba sin reducir el entrenamiento a menos de 100 filas (prioridad: media).

## Limitaciones de esta auditoría

- No se ejecutó ningún script (regla 1): las cifras son las guardadas en `resultados.json`; no se verificó que se regeneren.
- No se leyeron `tests/` ni `evidencia/salida_entrenar.txt`; se auditó el código de `src/` y `resultados.json`.
- `resultados.json` se leyó hasta la línea 400 de su sección de K-Means; el resto no afecta a ningún criterio.
- Fuera de los 15 criterios: la silueta guardada (`0.2848589`) es 0.00004 menor que la del piloto (0.2849); la prueba `test_errores_segmentacion.py` la acepta con una tolerancia de 5e-5, lo que conviene decir con claridad en el README.
- No existe documento de apoyo con costos, variables prohibidas o momento en que se conoce cada columna (V1.5, V3.2, V6.1 se apoyan en las docstrings del código).
