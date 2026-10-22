# Clasificador de perfil químico de lotes — Dilitio Wine Corp

Herramienta que, a partir de 13 mediciones químicas de un lote de vino, indica a cuál de tres perfiles químicos se parece
(`class_0`, `class_1`, `class_2`) y cuánto confía en ello; la usa quien decide a qué línea de producto va cada lote.
Capstone de MAI 540 (Atlantis University), continuación del servidor MCP de los Módulos 5.1 y 5.2.

## Problema

Dilitio Wine Corp quiere decidir de forma objetiva qué línea de producto (entrada, revisión de proceso o premium) le
corresponde a cada lote, y hoy no hay datos de cómo se decide. El piloto del Módulo 5.2 mostró que la química separa tres
perfiles. Esta herramienta convierte ese hallazgo en algo que se puede preguntar lote por lote: **¿a qué perfil químico se
parece este lote?** Apoya la decisión; no la toma. La correspondencia perfil → línea de producto no existe en los datos y
debe definirla la empresa (ver Limitaciones).

**Costo de los errores (declaración del proyecto).** Dilitio Wine Corp no entregó una matriz de costos y aquí no se
supone ninguna: se trata cada error por igual. Por eso la métrica de decisión es la **F1 macro**, que da el mismo peso a
las tres clases, y la exactitud se reporta junto a la línea base «siempre la clase mayoritaria». Si la empresa dice que un
tipo de error cuesta más (por ejemplo, un lote premium enviado a la línea de entrada), habría que cambiar la métrica.

## Datos

- **Fuente:** UCI Machine Learning Repository, *Wine* (Aeberhard y Forina, 1991), DOI 10.24432/C5PC7J. Copia local en
  `datos/wine.csv`, la misma que usa el piloto (`datasets/wine.csv` del Módulo 5).
- **Permiso de uso:** conjunto público, publicado en UCI bajo licencia Creative Commons Atribución 4.0 (CC BY 4.0); se
  cita la fuente arriba. Conviene confirmar la licencia en la página del conjunto antes de redistribuirlo. No contiene
  datos personales ni de clientes, y no son datos de la empresa: no hay precios, ventas ni clientes.
- **Descripción:** 178 muestras, 13 variables numéricas de laboratorio (alcohol, ácido málico, ceniza, alcalinidad,
  magnesio, fenoles totales, flavonoides, fenoles no flavonoides, proantocianinas, intensidad de color, tono,
  OD280/OD315 y prolina) y la variable objetivo `cultivar` (`class_0` = 59, `class_1` = 71, `class_2` = 48). Se usa
  `cultivar` como etiqueta del perfil químico. Las 13 variables son mediciones: se conocen al analizar el lote, antes de
  clasificarlo, y ninguna se calcula a partir de la etiqueta.

## Cómo funciona

```
datos/wine.csv ─► validar ─► partición 80/20 estratificada ─┬─► 80 %: validación cruzada 5×3 de
                                                              │   línea base + 4 modelos (Pipeline)
                                                              │         │
                                                              │   criterio de selección ─► modelo elegido
                                                              │
                                                              └─► 20 %: prueba final (una sola medición)
modelo elegido ─► ajustado con los 178 lotes ─► modelos/modelo_final.joblib ─► predecir.py / servidor MCP
```

1. `src/entrenar.py` aparta una **prueba final** (20 %, 36 lotes, estratificada, semilla 42) que no interviene en ninguna decisión.
2. Con el 80 % restante (142 lotes) corre una **validación cruzada estratificada 5 pliegues × 3 repeticiones** (15
   estimaciones por modelo) para una **línea base** (`DummyClassifier`, siempre la clase mayoritaria) y cuatro modelos:
   regresión logística, árbol (profundidad 3), Random Forest y boosting. El escalado va dentro del `Pipeline`, así que se
   ajusta solo con los datos de entrenamiento de cada pliegue. Los hiperparámetros están fijos (no se afinó nada).
3. **Criterio de selección** (`src/seleccion.py`, escrito antes de mirar la prueba): se descarta todo modelo que no supere
   a la línea base por al menos 0.10 de F1 macro; entre los que quedan, se toma el de mayor media; los que quedan a menos de
   una desviación del mejor se consideran equivalentes y **se elige el más simple** (regresión logística < árbol < Random
   Forest < boosting). Con 178 lotes, una diferencia menor que una desviación es ruido, y un modelo simple es más fácil de
   explicar, auditar y mantener.
4. El elegido se mide **una vez** en la prueba final, se analizan sus errores por categoría y se ajusta de nuevo con los 178 lotes
   para el uso (las cifras de la prueba corresponden al modelo ajustado solo con el entrenamiento, no a este).
5. `src/segmentacion.py` repite el K-Means exploratorio de la propuesta (k = 3), ajustado solo con el entrenamiento, y
   verifica sus criterios (a) silueta ≥ 0.2849 y (b) estabilidad.
6. `src/predecir.py` y `src/mcp_server.py` (tools `clasificar_lote` y `resumen_validacion`) usan el modelo guardado. Si un
   valor del lote sale del rango visto en el entrenamiento, clasifican igual pero devuelven una advertencia.

## Resultados

Validación cruzada 5×3 sobre 142 lotes (media ± desviación estándar de 15 estimaciones) y prueba final de 36 lotes. Cifras
completas en `evidencia/resultados.md`.

| Modelo | Exactitud (media ± desviación) | F1 macro (media ± desviación) | Observación |
|---|---|---|---|
| Línea base (clase mayoritaria) | 0.401 ± 0.011 | 0.191 ± 0.004 | Piso: acertar sin mirar la química. En la prueba: 0.389. |
| Regresión logística | **0.981 ± 0.022** | **0.981 ± 0.022** | **Elegido.** Mejor media y el más simple. Prueba final: 0.972 (35 de 36). |
| Random Forest | 0.981 ± 0.026 | 0.981 ± 0.026 | Equivalente, más complejo. |
| Boosting | 0.958 ± 0.033 | 0.959 ± 0.033 | Fuera de la zona de equivalencia. |
| Árbol (profundidad 3) | 0.918 ± 0.046 | 0.921 ± 0.045 | El menos estable. |

**Errores por categoría.** En las predicciones fuera de pliegue (142 lotes) hay 3 errores, todos de `class_1`
(recall 0.947): dos se confunden con `class_0` y uno con `class_2`; `class_0` y `class_2` tienen recall 1.000. En la
prueba final hay 1 error de 36: un lote de `class_2` clasificado como `class_1` (recall de `class_2` = 0.900). `class_1` es
la clase del medio en la química, y por eso la que más se confunde con las otras dos. Con 10 a 14 lotes por clase en la
prueba, un solo error mueve el recall de una clase en 7 a 10 puntos: la comparación por clase es indicativa, no concluyente.

**K-Means exploratorio (k = 3, ajustado con el entrenamiento).** Silueta 0.2875 (piloto 0.2849: se cumple el criterio a);
estabilidad por remuestreo, ARI 0.945 ± 0.031 (mínimo 0.894: se cumple el criterio b); acuerdo con `cultivar` en lotes que
K-Means no vio, ARI 0.909.

**Advertencia sobre estas cifras.** Este conjunto es famoso por ser fácil: casi cualquier modelo razonable supera 0.9. Una
exactitud de 0.98 aquí no demuestra que la herramienta funcione con los vinos de Dilitio Wine Corp.

## Instalación

Requisitos: Python 3.10 o superior (probado con 3.14) y Git.

```bash
git clone https://github.com/mikecrv2019-bit/MAI540---MODULO-5.git
cd MAI540---MODULO-5/Modulo 8_1
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Opcional (recomendado si va a hacer commits): instalar el hook que ejecuta las pruebas antes de cada commit.

```bash
python instalar_hook.py
```

## Cómo ejecutar

Todos los comandos se ejecutan desde la carpeta `Modulo 8_1/`.

1. Entrenar, validar y guardar la evidencia (tarda unos segundos):

   ```bash
   python src/entrenar.py
   ```

   Se debe ver el informe de resultados: la tabla de validación cruzada con la línea base en 0.191 de F1 macro y la
   regresión logística en 0.981 ± 0.022, la línea `Elegido: regresion_logistica`, la prueba final (exactitud 0.972) y, al
   final, `Modelo guardado en modelos/modelo_final.joblib`. Se actualizan `evidencia/resultados.json` y `resultados.md`.

2. Clasificar un lote (el 0 del archivo de datos, o uno propio en JSON con las 13 variables):

   ```bash
   python src/predecir.py --fila 0
   ```

   Se debe ver `"perfil": "class_0"` con probabilidad 0.9998 y `"advertencias": []`.

3. Opcional, como servidor MCP (Inspector en el navegador; necesita Node.js):

   ```bash
   mcp dev src/mcp_server.py
   ```

## Pruebas

```bash
pytest -v
```

Se esperan **20 pruebas en verde** (unos 10 segundos). Comprueban: forma y validación de los datos (no se acepta NaN ni
columnas faltantes); partición estratificada y sin traslape; que el escalador aprende solo del entrenamiento (sin fuga);
que la validación cruzada es determinista y tiene 15 estimaciones; el criterio de selección con resultados sintéticos; que el
modelo elegido supera a la línea base, que su desviación es ≤ 0.05 y que la prueba final lo confirma; el análisis de
errores con un caso calculado a mano; los criterios del K-Means; y la herramienta de uso (entradas inválidas, advertencia
de rango, servidor MCP). La salida completa guardada está en `evidencia/pytest_v_final.txt`.

## Limitaciones

- **No usar como decisión comercial automática.** El modelo predice el *cultivar* del archivo de UCI, usado como sustituto
  del perfil químico; no hay datos de qué lote Dilitio Wine Corp vende como «entrada», «revisión» o «premium». Esa
  correspondencia hay que definirla con un enólogo de la empresa antes de usar la salida para algo más que describir.
- **No usar con vinos que no se parezcan al conjunto** (otras regiones, uvas o métodos de laboratorio): las 178 muestras
  son públicas, de tres cultivares, y no representan la producción de la empresa. La herramienta avisa si un valor sale del
  rango de entrenamiento, pero no detecta un cambio en la relación entre variables.
- **Muestra pequeña.** 142 lotes para validar y 36 para la prueba; con 10 a 14 lotes por clase en la prueba ninguna clase
  alcanza los 20 casos que pide la Skill de auditoría para comparar clases (hallazgo V4.2, explicado en `auditorias/`).
- **Datos que cambian con el tiempo:** cosechas, proveedores o el método de medición moverían las distribuciones (por
  ejemplo, prolina y magnesio dependen del método). Se notaría porque aparecen advertencias de rango o porque baja la
  exactitud al reevaluar con lotes nuevos etiquetados.
- **Cuándo reentrenar:** al incorporar datos reales de la empresa, al cambiar el método de medición o si la exactitud sobre
  lotes nuevos cae más de 0.05 respecto a la validación cruzada (0.981 ± 0.022).
- La silueta de K-Means (≈ 0.29) indica grupos que se traslapan; el K-Means es exploratorio y no alimenta al clasificador.

## Auditoría y revisión de cambios

La Skill `auditoria-modelos` v2.0 se aplicó dos veces; informes y resoluciones en `auditorias/` y `revision/`. El historial de
decisiones, instrucciones y verificaciones está en `BITACORA.md`.

## Estructura del repositorio

```
Modulo 8_1/
├── README.md
├── BITACORA.md                  instrucciones, verificaciones y correcciones
├── requirements.txt
├── instalar_hook.py             instala el hook pre-commit
├── hooks/pre-commit             pytest + búsqueda de claves antes de cada commit
├── datos/wine.csv               datos (UCI Wine, CC BY 4.0)
├── src/                         datos, modelos, validación, selección, errores, K-Means, entrenar, predecir, servidor MCP
├── tests/                       20 pruebas con pytest
├── evidencia/                   resultados, salida de pytest -v y del hook
├── auditorias/                  informes de la Skill de auditoría
├── revision/                    texto de los pull requests con su revisión
└── .claude/skills/auditoria-modelos/   la Skill (Módulo 4)
```

## Autor

mikecrv2019 · MAI 540: Machine Learning · Atlantis University · 22 de octubre de 2026.
