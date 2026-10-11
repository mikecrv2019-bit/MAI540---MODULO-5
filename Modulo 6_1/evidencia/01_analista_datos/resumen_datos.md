# Resumen de datos · German Credit

Archivo: `datos/credit_g.csv`. Generado por `src/analisis_datos.py` (todas las cifras provienen de ese cálculo).

## Forma y tipos

- Forma de `X`: **1000 filas x 20 columnas**.
- Categóricas (13): checking_status, credit_history, purpose, savings_status, employment, personal_status, other_parties, property_magnitude, other_payment_plans, housing, job, own_telephone, foreign_worker.
- Numéricas (7): duration, credit_amount, installment_commitment, residence_since, age, existing_credits, num_dependents.

## Variable objetivo (`clase`; 1 = bad, 0 = good)

| Clase | Filas | Proporción |
|---|---|---|
| good (0) | 700 | 70.0% |
| bad (1) | 300 | 30.0% |

**Línea base «siempre bueno»: exactitud = 0.7000** (70.0%).

## Calidad

- Valores faltantes en `X`: 0; en `y`: 0.
- Filas duplicadas en `X`: 0; duplicadas incluyendo la clase: 0; filas con `X` idéntico y clase distinta: 0.

## Variables categóricas (cardinalidad y tasa de `bad`)

| Columna | Cardinalidad | Categorías (n; tasa bad) |
|---|---|---|
| checking_status | 4 | no checking (394; 0.12); <0 (274; 0.49); 0<=X<200 (269; 0.39); >=200 (63; 0.22) |
| credit_history | 5 | existing paid (530; 0.32); critical/other existing credit (293; 0.17); delayed previously (88; 0.32); all paid (49; 0.57); no credits/all paid (40; 0.62) |
| purpose | 10 | radio/tv (280; 0.22); new car (234; 0.38); furniture/equipment (181; 0.32); used car (103; 0.17); business (97; 0.35); education (50; 0.44); repairs (22; 0.36); domestic appliance (12; 0.33); other (12; 0.42); retraining (9; 0.11) |
| savings_status | 5 | <100 (603; 0.36); no known savings (183; 0.17); 100<=X<500 (103; 0.33); 500<=X<1000 (63; 0.17); >=1000 (48; 0.12) |
| employment | 5 | 1<=X<4 (339; 0.31); >=7 (253; 0.25); 4<=X<7 (174; 0.22); <1 (172; 0.41); unemployed (62; 0.37) |
| personal_status | 4 | male single (548; 0.27); female div/dep/mar (310; 0.35); male mar/wid (92; 0.27); male div/sep (50; 0.40) |
| other_parties | 3 | none (907; 0.30); guarantor (52; 0.19); co applicant (41; 0.44) |
| property_magnitude | 4 | car (332; 0.31); real estate (282; 0.21); life insurance (232; 0.31); no known property (154; 0.44) |
| other_payment_plans | 3 | none (814; 0.28); bank (139; 0.41); stores (47; 0.40) |
| housing | 3 | own (713; 0.26); rent (179; 0.39); for free (108; 0.41) |
| job | 4 | skilled (630; 0.30); unskilled resident (200; 0.28); high qualif/self emp/mgmt (148; 0.34); unemp/unskilled non res (22; 0.32) |
| own_telephone | 2 | none (596; 0.31); yes (404; 0.28) |
| foreign_worker | 2 | yes (963; 0.31); no (37; 0.11) |

## Variables numéricas (rangos)

| Columna | Mín | Máx | Media | Mediana | Desv. est. | Únicos | Asimetría | Atípicos IQR |
|---|---|---|---|---|---|---|---|---|
| duration | 4 | 72 | 20.90 | 18 | 12.06 | 33 | 1.09 | 70 |
| credit_amount | 250 | 18424 | 3271.26 | 2319.5 | 2822.74 | 921 | 1.95 | 72 |
| installment_commitment | 1 | 4 | 2.97 | 3 | 1.12 | 4 | -0.53 | 0 |
| residence_since | 1 | 4 | 2.85 | 3 | 1.10 | 4 | -0.27 | 0 |
| age | 19 | 75 | 35.55 | 33 | 11.38 | 53 | 1.02 | 23 |
| existing_credits | 1 | 4 | 1.41 | 1 | 0.58 | 4 | 1.27 | 6 |
| num_dependents | 1 | 2 | 1.16 | 1 | 0.36 | 2 | 1.91 | 155 |

## Anomalías y observaciones

- 'purpose' tiene categorias con <= 10 filas: {'retraining': 9}.
- Columnas numericas con <= 5 valores distintos (discretas/ordinales, tratables como categoricas): ['installment_commitment', 'residence_since', 'existing_credits', 'num_dependents'].
- 'duration' es asimetrica (asimetria=1.0942, max=72.0, mediana=18.0, 70 atipicos IQR).
- 'credit_amount' es asimetrica (asimetria=1.9496, max=18424.0, mediana=2319.5, 72 atipicos IQR).
- 'age' es asimetrica (asimetria=1.0207, max=75.0, mediana=33.0, 23 atipicos IQR).
- 'existing_credits' es asimetrica (asimetria=1.2726, max=4.0, mediana=1.0, 6 atipicos IQR).
- 'num_dependents' es asimetrica (asimetria=1.9094, max=2.0, mediana=1.0, 155 atipicos IQR).
- Clase desbalanceada: bad=300 (30.0%) frente a good=700; una exactitud <= 70.0% no supera la linea base trivial.
- No se hallaron duplicados ni faltantes: no se propone limpiar filas.
- Hay categorias con texto literal 'none' (valor valido, no faltante): {'other_parties': 907, 'other_payment_plans': 814, 'own_telephone': 596}. cargar_datos() las conserva como texto.

## Instrucciones para el ingeniero de modelos

1. Usar siempre cargar_datos() de src/datos.py; X llega sin transformar.
2. Codificar las categoricas (cols_cat) y escalar las numericas SOLO dentro de un Pipeline (p. ej. ColumnTransformer), de modo que el ajuste ocurra unicamente con los datos de entrenamiento de cada particion.
3. Definir las particiones (validacion cruzada y/o train/test) en su propio modulo, estratificadas por y, con semillas fijas.
4. Comparar toda exactitud contra la linea base «siempre bueno» (70.0%); reportar tambien metricas sensibles a la clase minoritaria (recall/F1/AUC de 'bad').
5. No modificar datos/credit_g.csv. Cualquier limpieza propuesta debe reportarse; aqui no se propone ninguna fila a eliminar.
6. Propuesta (no aplicada): considerar tratar como categoricas las numericas discretas listadas en las anomalias y/o transformar logaritmicamente credit_amount y duration dentro del Pipeline, a criterio del ingeniero.
