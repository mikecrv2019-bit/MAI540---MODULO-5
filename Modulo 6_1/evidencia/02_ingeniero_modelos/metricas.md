# Metricas del ingeniero de modelos

Generado por `src/ejecutar_ingeniero.py` (todas las cifras provienen de ese calculo; determinista).

- Datos: 1000 filas, 13 categoricas y 7 numericas. Clase positiva: bad (y=1).
- Linea base «siempre bueno»: exactitud = 0.70 (calculada: 0.7000).
- Validacion cruzada: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`.
- Particion unica: `train_test_split(test_size=0.25, stratify=y, random_state=s)`, semillas 0 a 29 (y subconjunto 0 a 9).
- Modelos: DecisionTreeClassifier(random_state=42); RandomForestClassifier(random_state=42); resto por defecto.
- Preprocesamiento (dentro del Pipeline): ColumnTransformer: OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1) en categoricas; numericas 'passthrough'.
- Dispersion: desviacion estandar muestral (ddof=1).

## 1. Validacion cruzada (5 pliegues)

| Modelo | Exactitud media | Exactitud desv. | Recall bad media | Recall bad desv. | Recall bad agregado (cross_val_predict, dato adicional) |
|---|---|---|---|---|---|
| Arbol de decision | 0.6980 | 0.0189 | 0.5300 | 0.0462 | 0.5300 |
| Random Forest | 0.7590 | 0.0065 | 0.3767 | 0.0190 | 0.3767 |

Valores por pliegue:

| Modelo | Metrica | P1 | P2 | P3 | P4 | P5 |
|---|---|---|---|---|---|---|
| Arbol de decision | Exactitud | 0.7100 | 0.7100 | 0.6650 | 0.7050 | 0.7000 |
| Arbol de decision | Recall bad | 0.5333 | 0.5667 | 0.4500 | 0.5500 | 0.5500 |
| Random Forest | Exactitud | 0.7650 | 0.7650 | 0.7500 | 0.7600 | 0.7550 |
| Random Forest | Recall bad | 0.3667 | 0.3833 | 0.4000 | 0.3833 | 0.3500 |

## 2. Particion unica 75/25, semillas 0 a 29

| Modelo | Metrica | Min | Max | Media | Desv. | Media - media CV (pp) | Min - media CV (pp) | Max - media CV (pp) |
|---|---|---|---|---|---|---|---|---|
| Arbol de decision | Exactitud | 0.6080 | 0.7200 | 0.6808 | 0.0228 | -1.72 | -9.00 | +2.20 |
| Arbol de decision | Recall bad | 0.3467 | 0.6533 | 0.4844 | 0.0714 | -4.56 | -18.33 | +12.33 |
| Random Forest | Exactitud | 0.7120 | 0.8040 | 0.7516 | 0.0238 | -0.74 | -4.70 | +4.50 |
| Random Forest | Recall bad | 0.2800 | 0.5067 | 0.3769 | 0.0639 | +0.02 | -9.67 | +13.00 |

## 3. Particion unica 75/25, solo semillas 0 a 9

| Modelo | Metrica | Min | Max | Media | Desv. | Media - media CV (pp) | Min - media CV (pp) | Max - media CV (pp) |
|---|---|---|---|---|---|---|---|---|
| Arbol de decision | Exactitud | 0.6080 | 0.7200 | 0.6744 | 0.0307 | -2.36 | -9.00 | +2.20 |
| Arbol de decision | Recall bad | 0.3600 | 0.6533 | 0.5093 | 0.0795 | -2.07 | -17.00 | +12.33 |
| Random Forest | Exactitud | 0.7120 | 0.7960 | 0.7532 | 0.0278 | -0.58 | -4.70 | +3.70 |
| Random Forest | Recall bad | 0.2933 | 0.5067 | 0.3813 | 0.0734 | +0.47 | -8.33 | +13.00 |

Rango de la particion unica frente a la media CV: [min - media CV, max - media CV] en puntos porcentuales (pp), columnas finales de las tablas.

## 4. Comparacion con la linea base

- Arbol de decision: exactitud media CV = 0.6980 frente a la linea base 0.70 (diferencia -0.20 pp).
- Random Forest: exactitud media CV = 0.7590 frente a la linea base 0.70 (diferencia +5.90 pp).

## 5. Decisiones tomadas

1. Parametros por defecto de scikit-learn salvo `random_state=42`; no hubo busqueda de hiperparametros.
2. Unico preprocesamiento: `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)` en las 13 categoricas y `passthrough` en las 7 numericas, dentro del Pipeline (se ajusta en cada pliegue/particion de entrenamiento).
3. Por indicacion del orquestador no se aplico escalado, logaritmos ni tratamiento de las numericas discretas como categoricas (propuestas del analista, no aplicadas).
4. Recall de bad en CV calculado por pliegue (`scoring='recall'`, positivo = 1); el recall agregado de `cross_val_predict` se reporta solo como dato adicional.
5. Desviacion estandar muestral (ddof=1) en todas las tablas; la CV usa 5 valores y las particiones 30 (o 10) valores.
6. La CV y el `cross_val_predict` usan el mismo objeto `StratifiedKFold` con semilla 42, por lo que generan los mismos pliegues.
7. La semilla del modelo (42) es fija en todas las particiones; solo cambia la semilla de la particion (0..29).
8. `src/datos.py` y `datos/credit_g.csv` no se modificaron.

## 6. Qué debe verificar el auditor

Afirmaciones concretas de este entregable:

1. Los dos modelos son `DecisionTreeClassifier(random_state=42)` y `RandomForestClassifier(random_state=42)` con el resto por defecto.
2. La CV es `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` y el preprocesamiento esta dentro del Pipeline (sin fuga: no se transforma nada fuera de el).
3. Las particiones usan `train_test_split(test_size=0.25, stratify=y, random_state=s)` con s = 0..29.
4. El recall de bad por pliegue usa la clase y=1 como positiva; la media/desv. son de los 5 recalls por pliegue.
5. Cifras a reproducir: Arbol de decision exactitud CV 0.6980 +/- 0.0189, recall bad CV 0.5300 +/- 0.0462; Random Forest exactitud CV 0.7590 +/- 0.0065, recall bad CV 0.3767 +/- 0.0190.
6. Las diferencias en pp se calculan restando la media CV a la media/min/max de las particiones unicas (columnas de las secciones 2 y 3).
7. La ejecucion es determinista: volver a correr `python src/ejecutar_ingeniero.py` debe regenerar `metricas.json` y `metricas.md` identicos.
8. El script no modifica `src/datos.py` ni `datos/credit_g.csv`.
