# Errores por categoria con los 178 lotes (generado por `src/detalle_errores.py`)

Modelo: `regresion_logistica`. Validacion cruzada estratificada 5x3 sobre los 178 lotes; cada lote lo predice un modelo que no lo vio. Las tablas usan la repeticion 1 (cada lote cuenta una vez).

Errores en la repeticion 1: **3 de 178**. Lotes que fallan en al menos una de las 3 repeticiones: **3**.

## Por clase real

| Clase | n | Errores | Recall | IC 95 % del recall | Errores estables (2 o 3 repeticiones) |
|---|---|---|---|---|---|
| class_0 | 59 | 0 | 1.000 | 0.939 a 1.000 | 0 |
| class_1 | 71 | 2 | 0.972 | 0.903 a 0.992 | 2 |
| class_2 | 48 | 1 | 0.979 | 0.891 a 0.996 | 0 |

## Por tercil de `alcohol`

| Grupo | n | Errores | Tasa de error | IC 95 % (Wilson) |
|---|---|---|---|---|
| alcohol 11.03 a 12.52 | 60 | 1 | 0.017 | 0.003 a 0.089 |
| alcohol 12.52 a 13.48 | 59 | 2 | 0.034 | 0.009 a 0.115 |
| alcohol 13.48 a 14.83 | 59 | 0 | 0.000 | 0.000 a 0.061 |

## Por tercil de `proline`

| Grupo | n | Errores | Tasa de error | IC 95 % (Wilson) |
|---|---|---|---|---|
| proline 278 a 560 | 61 | 1 | 0.016 | 0.003 a 0.087 |
| proline 560 a 835 | 58 | 2 | 0.034 | 0.010 a 0.117 |
| proline 835 a 1680 | 59 | 0 | 0.000 | 0.000 a 0.061 |

## Por tercil de `magnesium`

| Grupo | n | Errores | Tasa de error | IC 95 % (Wilson) |
|---|---|---|---|---|
| magnesium 70 a 92 | 63 | 2 | 0.032 | 0.009 a 0.109 |
| magnesium 92 a 103 | 58 | 0 | 0.000 | 0.000 a 0.062 |
| magnesium 103 a 162 | 57 | 1 | 0.018 | 0.003 a 0.093 |

## Por confianza de la prediccion

| Grupo | n | Errores | Tasa de error | IC 95 % (Wilson) |
|---|---|---|---|---|
| confianza 0.00 a 0.80 | 12 | 3 | 0.250 | 0.089 a 0.532 |
| confianza 0.80 a 0.90 | 8 | 0 | 0.000 | 0.000 a 0.324 |
| confianza 0.90 a 0.99 | 53 | 0 | 0.000 | 0.000 a 0.068 |
| confianza 0.99 a 1.00 | 105 | 0 | 0.000 | 0.000 a 0.035 |

Confianza mas alta de un lote mal clasificado: 0.677.

## Lotes mal clasificados (repeticion 1)

- Lote 68: real `class_1`, predicho `class_2`, confianza 0.411, probabilidad de su clase real 0.221, fallo en 2 de 3 repeticiones. Se parece mas a la clase predicha en: alcohol (z=1.97 en su clase, z=0.35 en la predicha); od280/od315_of_diluted_wines (z=1.72 en su clase, z=0.91 en la predicha); nonflavanoid_phenols (z=1.5 en su clase, z=0.83 en la predicha).
- Lote 83: real `class_1`, predicho `class_2`, confianza 0.675, probabilidad de su clase real 0.316, fallo en 3 de 3 repeticiones. Se parece mas a la clase predicha en: malic_acid (z=1.9 en su clase, z=0.48 en la predicha); alcohol (z=1.43 en su clase, z=0.2 en la predicha); total_phenols (z=1.12 en su clase, z=0.08 en la predicha).
- Lote 134: real `class_2`, predicho `class_1`, confianza 0.677, probabilidad de su clase real 0.316, fallo en 1 de 3 repeticiones. Se parece mas a la clase predicha en: malic_acid (z=1.92 en su clase, z=0.68 en la predicha); ash (z=1.01 en su clase, z=0.02 en la predicha); alcalinity_of_ash (z=1.73 en su clase, z=0.82 en la predicha).
