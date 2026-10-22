# Informe de auditoría — Capstone Dilitio Wine Corp (rama `feat/herramienta-readme`, estado final)

- **Archivos auditados:** `Modulo 8_1/src/datos.py`, `modelos.py`, `validacion.py`, `seleccion.py`, `errores.py`, `segmentacion.py`, `entrenar.py`, `predecir.py`; salida guardada `Modulo 8_1/evidencia/resultados.json`
- **Archivos de apoyo leídos:** `Modulo 8_1/README.md`
- **Columna objetivo:** `cultivar` — codificación: texto, `class_0`, `class_1`, `class_2` (evidencia: `datos.py:16` `CLASES = ["class_0", "class_1", "class_2"]`; carga en `datos.py:43` `return df[PREDICTORAS].copy(), df[OBJETIVO].copy()`)
- **Tipo de problema:** clasificación multiclase, 3 clases (evidencia: `modelos.py:21` `DummyClassifier(strategy="most_frequent")`, `modelos.py:24` `LogisticRegression(max_iter=1000, random_state=SEMILLA)`)
- **Subgrupos:** `cultivar` (origen: argumento). Es la propia variable objetivo (categorías); el proyecto no tiene atributos protegidos (`README.md:27-31`, 13 mediciones químicas).
- **Skill:** auditoria-modelos v2.0 — fecha: 2026-10-22
- **Modificaciones al proyecto:** ninguna (auditoría de solo lectura)

Desbalance (paso previo): `71/48 = 1.4792 < 1.5` con la distribución `README.md:29` (`class_0` = 59, `class_1` = 71, `class_2` = 48) y `resultados.json` → **sin desbalance** según la definición de la Skill.

## Resumen

| Verificación | Resultado |
|---|---|
| V1 Métricas reportadas | NO SE PUEDE DETERMINAR |
| V2 Partición de datos | PASA |
| V3 Fuga de información | PASA |
| V4 Disparidad entre subgrupos | NO SE PUEDE DETERMINAR |
| V5 Validez de datos de entrada | PASA |
| V6 Variables no admisibles | PASA |

## Tabla de verificación

| ID | Verificación | Resultado | Evidencia | Observación |
|---|---|---|---|---|
| V1.1 | Rango válido | PASA | `resultados.json:64` `"media": 0.9812807881773398`; `resultados.json:272` `"exactitud": 0.9722222222222222` | Todas las exactitudes, F1, recall y precisión guardados (`resultados.json:15-373`) están en [0, 1]; ninguna es NaN. |
| V1.2 | Consistencia con la matriz | PASA | Matriz de prueba `resultados.json:335-351` (`[12,0,0],[0,14,0],[0,1,9]`) y `resultados.json:272` | Exactitud `(12+14+9)/36 = 0.9722` (reportada 0.9722). Precisión class_1 `14/(14+1) = 0.9333` (`:367`). Recall class_2 `9/10 = 0.9` (`:372`). F1 macro `(1.0+0.9655+0.9474)/3 = 0.9710` (reportada 0.9710, `:273`). Matriz fuera de pliegue (`:277-292`): precisión class_0 `47/49 = 0.9592` (`:303`). La exactitud CV media (0.9813) es un promedio de 15 pliegues y no se deriva de esa matriz (una repetición): magnitudes distintas, no inconsistencia. |
| V1.3 | Clase positiva correcta | PASA | `errores.py:10` `cm = confusion_matrix(y_real, y_pred, labels=clases)` | Reporte por clase con etiqueta explícita (`errores.py:12-18`); F1 macro sin clase positiva (`validacion.py:46` `f1_score(y.iloc[te], p, average="macro")`). |
| V1.4 | No solo accuracy con desbalance | PASA | `71/48 = 1.4792 < 1.5` (`README.md:29`) | Sin desbalance reportar accuracy bastaría; además el código calcula F1 macro, recall y precisión por clase, matriz y línea base (`entrenar.py:40-42`). |
| V1.5 | Métrica acorde al costo | NO SE PUEDE DETERMINAR | `README.md:15-16` `no entregó una matriz de costos y aquí no se supone ninguna: se trata cada error por igual` | Multiclase sin clase de interés ni costos distintos por tipo de error. El proyecto lo declara explícitamente (F1 macro, `README.md:17`), pero la Skill exige un error más caro para decidir PASA. |
| V2.1 | División antes del preprocesamiento que aprende | PASA | `modelos.py:23` `("escalado", StandardScaler()),`; `validacion.py:43` `modelo = clone(estimador).fit(X.iloc[tr], y.iloc[tr])` | Clasificadores: el escalado va dentro del `Pipeline` y se ajusta por pliegue. K-Means: `segmentacion.py:31` `esc = StandardScaler().fit(X_tr)` y `entrenar.py:55` `segmentar(X_tr, y_tr, X_te, y_te)`; la prueba solo se transforma (`segmentacion.py:54`). El ajuste final con los 178 lotes (`entrenar.py:62` `final = clone(modelos[elegido]).fit(X, y)`) ocurre después de reportar toda métrica, está declarado (`README.md:55-56`) y ninguna cifra sale de él. |
| V2.2 | Semilla fija | PASA | `validacion.py:20` `random_state=SEMILLA`; `validacion.py:24` `random_state=SEMILLA`; `segmentacion.py:35` `rng = np.random.default_rng(SEMILLA)` | Semilla entera en partición, CV, modelos aleatorios (`modelos.py:24,27,30,33`) y KMeans (`segmentacion.py:20`). `DummyClassifier(most_frequent)` es determinista. El generador se crea dentro de `segmentar`. |
| V2.3 | Estratificación | PASA | `validacion.py:20` `stratify=y`; `validacion.py:24` `RepeatedStratifiedKFold(...)` | Clasificación: ambas particiones estratificadas. |
| V2.4 | Misma partición para los modelos comparados | PASA | `entrenar.py:28` `{nombre: evaluar_cv(est, X_tr, y_tr) for nombre, est in crear_modelos().items()}` | Mismo `X_tr`, `y_tr` y `crear_cv()` con semilla fija (`validacion.py:39`); las diferencias de preprocesamiento van dentro del `Pipeline`. |
| V3.1 | Nada se ajusta con datos de prueba | PASA | `entrenar.py:36` `cv = comparar_modelos(X_tr, y_tr)`; `entrenar.py:37` `decision = elegir_modelo(cv)` | La elección usa solo CV del entrenamiento; no se afinan hiperparámetros (valores fijos en `modelos.py`); la prueba se mide una vez (`entrenar.py:40`). K-Means ajustado solo con `X_tr` (`segmentacion.py:31,33`). |
| V3.2 | Ninguna columna posterior a la predicción | PASA | `datos.py:5` `13 predictoras se calcula a partir de la etiqueta (son mediciones de laboratorio)`; `README.md:30-31` `se conocen al analizar el lote, antes de clasificarlo` | Lista literal de 13 mediciones (`datos.py:17-21`), ninguna construida con `cultivar`. Exactitud de prueba 0.9722 (`resultados.json:272`), no 1.0. |
| V4.1 | Métrica por subgrupo | PASA | `errores.py:18` `por_clase[clase] = {"n": reales, "recall": recall, ...}`; `resultados.json:357-376` | Recall, precisión y F1 por cada valor de `cultivar` sobre la prueba final. |
| V4.2 | Disparidad dentro del umbral | NO SE PUEDE DETERMINAR | `resultados.json:359,365,371` `"n": 12`, `"n": 14`, `"n": 10` | Ninguna clase tiene ≥ 20 casos en la prueba (class_0 = 12, class_1 = 14, class_2 = 10). Complemento fuera del criterio: en la predicción fuera de pliegue (n = 47, 57, 38) los recall son 1.000, 0.947 y 1.000 contra `139/142 = 0.9789`; brecha máxima `0.9789 - 0.9474 = 0.0315 ≤ 0.10`. |
| V5.1 | Sin `inf`/`NaN` al entrenar | PASA | `datos.py:32` `if num.isna().any().any() or not np.isfinite(...)`; `entrenar.py:32` `X, y = cargar_datos()` | Sin divisiones ni `errors="coerce"`; `cargar_datos` llama a `validar_datos` (`datos.py:42`) en el flujo real. En uso, `predecir.py:37-40` rechaza valores no finitos. |
| V6.1 | Sin identificadores ni atributos prohibidos | PASA | `datos.py:17-21` lista `PREDICTORAS` | Ninguna predictora es un identificador (`alcohol`, `proline`, `flavanoids`, …) ni un atributo prohibido; `README.md:27-31` describe las 13 mediciones. |

## Acciones recomendadas

1. **[V1.5]** Obtener de Dilitio Wine Corp qué error cuesta más (por ejemplo, un lote premium enviado a la línea de entrada) y, si existe, cambiar la métrica prioritaria; mientras no haya costos, mantener la declaración de `README.md:15-18` (prioridad: media).
2. **[V4.2]** Con 36 filas de prueba ninguna clase llega a 20 casos; reportar la comparación por clase con predicciones fuera de pliegue (n ≥ 38) como evidencia complementaria y, si se consiguen más lotes, ampliar la prueba hasta ≥ 20 por clase (prioridad: media).

## Limitaciones de esta auditoría

- No se ejecutó ningún script (regla 1): las cifras son las guardadas en `resultados.json`.
- No se leyeron `tests/`, `mcp_server.py`, `verificar_servidor.py` ni el log del servidor; no entrenan ni evalúan el clasificador.
- `README.md:155` y `README.md:184` mencionan `evidencia/pytest_v_final.txt` y `BITACORA.md`, que no existían al momento de la auditoría; no afectan a ningún criterio.
- Fuera de los 15 criterios: la silueta del K-Means pasó a `0.28746` (`resultados.json:393`), mayor que la del piloto (0.2849), ahora sin tolerancia.
