# Busqueda de hiperparametros y comparacion de modelos (Tarea 6.2)

Generado por `src/busqueda_comparacion.py`; todas las cifras salen de `busqueda_comparacion.json`.

- Datos: 1000 filas; bad=300, good=700; linea base «siempre bueno» = 0.7000.
- Predictoras (18): sin age, personal_status (variables sensibles, solo para auditar).
- CV externa: `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`; CV interna: `StratifiedKFold(n_splits=5, shuffle=True, random_state=43)`.

## 1. Busqueda

Espacio: {'modelo__max_depth': [1, 2, 3, 4, 5, 7, 10, 'None'], 'modelo__min_samples_leaf': [1, 2, 5, 10, 20]} = 40 combinaciones.
Ganadora: {'max_depth': 5, 'min_samples_leaf': 5}.

| Medicion | Exactitud | Malos detectados |
|---|---|---|
| Arbol por defecto (CV) | 0.6900 | 0.4800 |
| Numero de la busqueda (optimista) | 0.7310 | 0.3233 |
| Anidada (honesta) | 0.7100 | 0.3567 |

Mejora optimista: +4.10 pp. Mejora honesta: +2.00 pp. Optimismo de la busqueda: +2.10 pp.

## 2. Comparacion con el mismo protocolo

| Modelo | Exactitud M (DE) | Malos detectados M (DE) | Ajuste (s/pliegue) |
|---|---|---|---|
| Árbol (por defecto) | 0.6900 (0.0127) | 0.4800 (0.0380) | 0.016 |
| Árbol afinado | 0.7100 (0.0334) | 0.3567 (0.1146) | 4.856 |
| Random Forest | 0.7650 (0.0200) | 0.4167 (0.0118) | 0.180 |
| HistGradientBoosting | 0.7660 (0.0108) | 0.5100 (0.0346) | 0.263 |
