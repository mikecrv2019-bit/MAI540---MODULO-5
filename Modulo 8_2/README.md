# Perfil químico de lotes de vino — Dilitio Wine Corp (demostración y análisis de errores)

Herramienta que, a partir de 13 mediciones de laboratorio de un lote de vino, dice a cuál de tres perfiles químicos se parece
y con cuánta confianza, y avisa cuando los datos que recibe ya no se parecen a los de entrenamiento. La usa quien decide a
qué línea de producto va cada lote. Capstone de MAI 540 (Atlantis University), Tarea 8.2: despliegue, errores por categoría y degradación.

**Valor en una frase:** convierte 13 números de laboratorio en un perfil con su confianza, y dice cuándo no hay que creerle.

## Problema

Dilitio Wine Corp quiere decidir de forma objetiva qué línea de producto (entrada, revisión de proceso o premium) le
corresponde a cada lote, y hoy no hay datos de cómo se decide. El piloto del Módulo 5.2 mostró que la química separa tres
perfiles. Esta herramienta lo convierte en una consulta lote por lote: **¿a qué perfil químico se parece este lote?** Apoya
la decisión; no la toma. La correspondencia perfil → línea de producto no existe en los datos y debe definirla la empresa.

**Costo de los errores.** La empresa no entregó una matriz de costos y aquí no se supone ninguna: todos los errores pesan
igual. Por eso la métrica de decisión es la F1 macro y la exactitud se reporta junto a una línea base.

## Datos

- **Fuente:** Aeberhard, S. y Forina, M. (1992). *Wine* [Conjunto de datos]. UCI Machine Learning Repository. https://doi.org/10.24432/C5PC7J
  (el repositorio registra la donación en 1991 y fija 1992 como año de cita; el README de la Tarea 8.1 decía 1991).
- **Permiso de uso:** Creative Commons Atribución 4.0 (CC BY 4.0), comprobado en la página del conjunto el 2026-10-23. Sin
  datos personales ni de clientes; no son datos de la empresa.
- **Descripción:** 178 muestras, 13 variables numéricas de laboratorio y la variable objetivo `cultivar` (`class_0` = 59,
  `class_1` = 71, `class_2` = 48), usada como etiqueta del perfil químico. No hay edad, sexo ni estado civil: el análisis por
  grupos se hace por clase y por tercil de variables químicas, no por características de personas.

## Cómo funciona

```
datos/wine.csv ─► validar ─► 80/20 estratificado ─┬─► 80 %: validación cruzada 5×3 (línea base + 4 modelos)
                                                    │        └─► criterio de selección ─► regresión logística
                                                    └─► 20 %: prueba final (una sola medición)
regresión logística ajustada con los 178 lotes ─► modelos/modelo_final.joblib
        ├─► app_gradio.py (pantalla) ─► src/interfaz.py ─► predecir.py + deriva.py
        ├─► src/predecir.py (línea de comandos) y src/mcp_server.py (tools MCP)
        └─► src/detalle_errores.py y src/simular_degradacion.py (evidencia de la Tarea 8.2)
```

- **Un lote:** devuelve el perfil, la probabilidad de cada perfil y avisos: confianza menor a 80 % o valores fuera del rango visto en el entrenamiento.
- **Archivo de lotes:** clasifica un CSV completo y mide la **deriva** contra los datos de entrenamiento con dos señales: lotes fuera de
  rango (alerta si pasan de 30 %) y prueba de Kolmogorov-Smirnov por variable con corrección de Bonferroni. Si el archivo trae
  `cultivar`, calcula también la exactitud real, que es la única señal que mide la degradación.
- El modelo se entrena solo la primera vez que se abre la app (unos segundos): `modelos/` no se versiona.

## Resultados

Validación cruzada 5×3 sobre 142 lotes (media ± desviación de 15 estimaciones) y prueba final de 36 lotes. Detalle en `evidencia/resultados.md`.

| Modelo | Exactitud (media ± desv.) | F1 macro (media ± desv.) | Observación |
|---|---|---|---|
| Línea base (clase mayoritaria) | 0.401 ± 0.011 | 0.191 ± 0.004 | Piso. En la prueba final: 0.389. |
| Regresión logística | **0.981 ± 0.022** | **0.981 ± 0.022** | **Elegido** (mejor media y el más simple). Prueba final: 0.972 (35 de 36). |
| Random Forest | 0.981 ± 0.026 | 0.981 ± 0.026 | Equivalente, más complejo. |
| Boosting | 0.958 ± 0.033 | 0.959 ± 0.033 | Fuera de la zona de equivalencia. |
| Árbol (profundidad 3) | 0.918 ± 0.046 | 0.921 ± 0.045 | El menos estable. |

Es un conjunto fácil: una exactitud de 0.98 no demuestra que sirva con los vinos de la empresa.

### Errores por categoría (178 lotes, predicción fuera de pliegue)

Cada lote lo predice un modelo que no lo vio. Detalle y lotes individuales en `evidencia/errores_detalle.md`. **3 errores de 178** (son los únicos 3 lotes que fallan en alguna de las tres repeticiones; uno falla en las 3, otro en 2 y otro en 1):

| Categoría | Casos | Errores | Qué muestra |
|---|---|---|---|
| `class_0` | 59 | 0 | Recall 1.000. |
| `class_1` | 71 | 2 | Recall 0.972: la clase del medio, la que se confunde con las otras dos. |
| `class_2` | 48 | 1 | Recall 0.979. |
| Confianza < 0.80 | 12 | **3** | Tasa de error 25 % (IC 95 %: 8.9 a 53.2 %); todos los errores están aquí. |
| Confianza ≥ 0.80 | 166 | 0 | Ningún error (IC 95 % superior: 2.3 %). |
| Terciles de alcohol, prolina y magnesio | 57 a 63 | 0 a 2 | Sin diferencias distinguibles (los IC se traslapan por completo). |

**Por qué creemos que ocurre.** Los tres lotes mal clasificados tienen una confianza máxima de 0.677 y valores (ácido málico, alcohol,
alcalinidad) más cercanos a la clase que el modelo predijo que a la suya: son lotes que se parecen a otro perfil. Con 3 errores,
la comparación entre grupos es indicativa, no concluyente: lo robusto es que **el error se concentra donde la confianza es baja**.
El umbral de 80 % se fijó viendo estos mismos 3 errores (todos bajo 0.68) de los 178 lotes, que incluyen los 36 de la prueba final
(hallazgo V3.1 de la auditoría, `auditorias/AUDIT_REPORT_8_2.md`): su capacidad real de atrapar errores futuros es optimista.

### Degradación simulada (`evidencia/degradacion.md`)

Mismo modelo, mismos lotes, pero medidos de otra manera (supuestos, no mediciones reales; 100 repartos, 133 lotes de entrenamiento y 45 de evaluación):

| Escenario | Exactitud | Alerta por distribución | Alerta por rango |
|---|---|---|---|
| Sin cambio | 0.983 ± 0.017 | 1 % (falsa alarma) | 0 % |
| Prolina +25 % | 0.970 ± 0.025 | 21 % | 9 % |
| Prolina +50 % | 0.943 ± 0.033 | 100 % | 49 % |
| Ruido de 0.5 desviaciones | 0.950 ± 0.030 | 6 % | 98 % |
| Ruido de 1.0 desviaciones | 0.871 ± 0.051 | 18 % | 100 % |

Las dos señales son complementarias: la de distribución ve el cambio de método (la media se corre) y casi no ve el ruido; la de rango
ve el ruido. Un cambio pequeño de prolina (+25 %) casi no baja la exactitud (−0.013) pero dispara alertas en uno de cada cinco repartos:
una alerta de deriva no equivale a una caída medida de exactitud.

## Instalación

Requisitos: Python 3.10 o superior (probado con 3.14) y Git. Este proyecto es la carpeta `Modulo 8_2/` de un repositorio que
guarda varios módulos; todo lo que necesita está dentro de esa carpeta.

```bash
git clone https://github.com/mikecrv2019-bit/MAI540---MODULO-5.git
cd MAI540---MODULO-5
git switch feat/despliegue-8-2        # quitar este paso cuando la rama esté integrada en main
cd "Modulo 8_2"
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si en Windows `python -m venv .venv` falla con `WinError 267`, la ruta es demasiado larga: clone en una carpeta corta (por ejemplo
`C:\proyectos`). La instalación tarda unos 2 o 3 minutos (Gradio es la dependencia más grande).

## Cómo ejecutar

Todos los comandos, desde la carpeta `Modulo 8_2/`.

**Opción A · App web local (la demostración):**

```bash
python app_gradio.py
```

Se imprime `Running on local URL: http://127.0.0.1:7860`. Ábrala en el navegador. La primera vez tarda unos segundos en entrenar. Verá:

1. En la pestaña **Un lote**, 13 campos con los valores típicos. Pulse **Lote ambiguo (el 83)** y luego **Clasificar lote**: aparece
   `class_1` con 66 % de confianza y el aviso «Confianza baja (< 80 %)». Con **Lote típico class_0**, 100 % y sin aviso.
2. En la pestaña **Archivo de lotes y control de deriva**, suba `datos/wine.csv` y pulse **Evaluar archivo**: 178 lotes
   clasificados (4 con confianza baja), exactitud 100 % (son los lotes con que se entrenó el modelo: no es una medida de generalización) y «Sin señales de deriva».

**Opción B · Línea de comandos, sin pantalla:**

```bash
python src/predecir.py --fila 83
```

Devuelve el perfil, las tres probabilidades (0.0104, 0.6608, 0.3289) y la lista de advertencias.

**Reproducir la evidencia:**

```bash
python src/entrenar.py              # resultados.md, resultados.json y el modelo
python src/detalle_errores.py       # errores_detalle.md, .json y errores_por_lote.csv
python src/simular_degradacion.py   # degradacion.md y .json (tarda menos de un minuto)
python src/figuras_informe.py       # las dos figuras del informe
```

## Pruebas

```bash
pytest -v
```

Se esperan **40 pruebas en verde** (unos 20 segundos); salida completa en `evidencia/pytest_v_final.txt`. Comprueban: validación de datos; partición
sin traslape y escalador sin fuga; validación cruzada determinista; el criterio de selección; que el modelo supere la línea base y su
prueba final; el análisis de errores (intervalo de Wilson contra un valor conocido, cada lote predicho una vez); la detección de
deriva (sin cambio no alerta, un sesgo de prolina se detecta y se nombra, pocos lotes solo miran el rango); la pantalla (lote típico,
lote ambiguo, campo vacío, valor fuera de rango, archivo inválido, archivo con la prolina desplazada) y las tools MCP.

## Limitaciones

Resumen; el detalle está en [`LIMITACIONES.md`](LIMITACIONES.md).

- **No usar como decisión comercial automática:** predice el `cultivar` de UCI, no la línea de producto de la empresa.
- **No usar con vinos que no se parezcan al conjunto** (otras regiones, uvas o métodos de laboratorio) ni sin mirar la confianza.
- **El modelo no avisa cuando se degrada.** Las alertas de deriva ayudan; la señal definitiva es la exactitud con lotes nuevos etiquetados.
- **Reentrenar** si la exactitud con lotes nuevos etiquetados cae más de 0.05 respecto a 0.981, si cambia el método de medición, o al incorporar datos reales de la empresa.

## Estructura del repositorio

```
Modulo 8_2/
├── README.md
├── LIMITACIONES.md              para qué no usarla, qué cambiaría con el tiempo, cómo se nota y cuándo reentrenar
├── BITACORA.md                  bitácora final de desarrollo asistido y reflexión
├── app_gradio.py                la pantalla web (Gradio)
├── requirements.txt
├── datos/wine.csv               datos (UCI Wine, CC BY 4.0)
├── src/                         modelo, validación, selección, errores, deriva, interfaz, servidor MCP, simulación
├── tests/                       40 pruebas con pytest
├── evidencia/                   resultados, errores por categoría, degradación, figuras y salida de pytest -v
├── revision/                    prueba de uso con otra persona
├── entrega/                     informe, presentación y bitácora en los formatos de Moodle
└── .claude/skills/auditoria-modelos/   la Skill de auditoría (Módulo 4)
```

## Autor

mikecrv2019 · MAI 540: Machine Learning · Atlantis University · 23 de octubre de 2026.
