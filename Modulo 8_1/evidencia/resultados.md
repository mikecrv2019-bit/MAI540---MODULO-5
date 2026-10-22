# Resultados del capstone (generado por `src/entrenar.py`)

Lotes: 178 (142 entrenamiento / 36 prueba final). Distribucion: {'class_0': 59, 'class_1': 71, 'class_2': 48}.

## Validacion cruzada 5 pliegues x 3 repeticiones (solo entrenamiento)

| Modelo | Exactitud (media ± desv.) | F1 macro (media ± desv.) |
|---|---|---|
| linea_base | 0.401 ± 0.011 | 0.191 ± 0.004 |
| regresion_logistica | 0.981 ± 0.022 | 0.981 ± 0.022 |
| arbol | 0.918 ± 0.046 | 0.921 ± 0.045 |
| random_forest | 0.981 ± 0.026 | 0.981 ± 0.026 |
| boosting | 0.958 ± 0.033 | 0.959 ± 0.033 |

**Regla:** F1 macro CV; superar la linea base por >= 0.1; entre los modelos a menos de 1 desviacion del mejor, el mas simple.

**Elegido:** `regresion_logistica` (mejor por media: `regresion_logistica`; piso de equivalencia 0.959; equivalentes: ['regresion_logistica', 'random_forest']).

## Prueba final (una sola medicion)

| Modelo | Exactitud | F1 macro |
|---|---|---|
| linea_base | 0.389 | 0.187 |
| regresion_logistica | 0.972 | 0.971 |

## Errores por categoria, predicciones fuera de pliegue (entrenamiento)

Errores: 3 de 142.

| Clase | n | Recall | Precision | F1 |
|---|---|---|---|---|
| class_0 | 47 | 1.000 | 0.959 | 0.979 |
| class_1 | 57 | 0.947 | 1.000 | 0.973 |
| class_2 | 38 | 1.000 | 0.974 | 0.987 |

Confusiones (real → predicho): class_1 → class_0: 2, class_1 → class_2: 1.

## Errores por categoria, prueba final

Errores: 1 de 36.

| Clase | n | Recall | Precision | F1 |
|---|---|---|---|---|
| class_0 | 12 | 1.000 | 1.000 | 1.000 |
| class_1 | 14 | 1.000 | 0.933 | 0.966 |
| class_2 | 10 | 0.900 | 1.000 | 0.947 |

Confusiones (real → predicho): class_2 → class_1: 1.

## K-Means exploratorio (k = 3)

- Silueta: 0.2849 (piloto 0.2849).
- Estabilidad (ARI en 30 remuestreos): 0.941 ± 0.042 (min 0.834).
- Acuerdo con `cultivar` (ARI): 0.897.
