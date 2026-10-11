# Tarea 6.2 · Optimización y auditoría del modelo (German Credit)

MAI 540 · Machine Learning · Atlantis University. Continúa la Tarea 6.1 (mismo dataset, misma validación cruzada,
mismas semillas). Dataset: `datos/credit_g.csv` (1,000 solicitudes, 20 variables, objetivo `clase`; `bad` = crédito malo).

## Costo de los errores (declaración del proyecto)

El enunciado de la Tarea 6.2 establece que en este dataset **aprobar un crédito malo cuesta más que rechazar uno
bueno**. En términos de la clase `bad` (positiva, `y = 1`): el falso negativo (aprobar un malo) es el error más caro
y el falso positivo (rechazar un bueno) el más barato. No se dispone de una matriz de costos numérica y no se
supone ninguna. Por eso la **métrica prioritaria es el recall de `bad`** (proporción de créditos malos detectados);
la exactitud se reporta junto a la línea base «siempre bueno» (0.70).

## Variables sensibles

`age` y `personal_status` se usan para **auditar, no para decidir**: no son predictoras. Detalle en `DESCRIPCION.md`.

## Qué hay en cada carpeta

| Ruta | Contenido |
|---|---|
| `src/datos.py`, `modelos.py`, `validacion.py` | Carga de datos, Pipeline (codificación dentro) y protocolo de evaluación único |
| `src/busqueda.py` | `GridSearchCV` del árbol (`max_depth` × `min_samples_leaf`) y validación cruzada anidada |
| `src/busqueda_comparacion.py` | Etapa 1: control de la 6.1, búsqueda, número honesto y comparación de tres modelos |
| `src/curvas.py`, `curvas_auditoria.py` | Etapa 2: curvas de aprendizaje y auditoría por subgrupo (edad, estado civil, vivienda) |
| `src/auditoria.py`, `interpretabilidad.py`, `config.py` | Recall por subgrupo, importancia por permutación y modelo elegido |
| `src/reproducir.py` | Corre las dos etapas desde cero y guarda sus salidas |
| `tests/test_modelo.py` | Pruebas automáticas con pytest |
| `evidencia/` | JSON y Markdown con todas las cifras, y la salida (`salida_*.txt`) de cada etapa |
| `figs/` | Curvas de aprendizaje |
| `.claude/skills/auditoria-modelos/` | Skill de auditoría del Módulo 4, v2.0 |
| `auditorias/` | Informe de la Skill sobre este proyecto |
| `informe/` | Informe técnico APA 7 (`generar_informe.py` lo regenera desde los JSON) |
| `BITACORA.md` | Instrucciones recibidas, verificaciones y correcciones |

## Reproducir desde cero

```bash
pip install -r requirements.txt
python src/reproducir.py        # ~2 min: regenera evidencia/ y figs/
python -m pytest -v             # 9 pruebas
python informe/generar_informe.py
```

Semillas: validación cruzada externa `StratifiedKFold(5, shuffle=True, random_state=42)` (igual que la 6.1); validación
interna de la búsqueda `StratifiedKFold(5, shuffle=True, random_state=43)`; modelos con `random_state=42`;
mezcla de la curva de aprendizaje `random_state=42`. Las cifras son deterministas; los tiempos de ajuste varían con el equipo.

## Protocolo

1. **Control**: se reproducen las cifras de la 6.1 con las 20 variables (árbol .698, Random Forest .759).
2. **Búsqueda**: 40 combinaciones (`max_depth` ∈ {1, 2, 3, 4, 5, 7, 10, None} × `min_samples_leaf` ∈ {1, 2, 5, 10, 20});
   elige por exactitud y registra el recall de `bad` de cada combinación.
3. **Medición honesta**: el número de la búsqueda (`best_score_`) es optimista; el honesto sale de la **validación
   cruzada anidada** (la búsqueda se repite dentro de cada pliegue externo con solo su entrenamiento).
4. **Comparación**: árbol afinado (número anidado), Random Forest e `HistGradientBoostingClassifier`, con el mismo `X`,
   la misma `y` y la misma validación cruzada. Random Forest e HGB van con parámetros por defecto (no se afinaron).
5. **Curva de aprendizaje**: la curva de la 6.1 no existía en ese repositorio (solo tenía validación cruzada y
   partición única); se **reconstruyó** con los modelos por defecto de la 6.1 y el mismo código que la curva nueva.
6. **Auditoría y pruebas**: Skill de auditoría v2.0 + 9 pruebas con pytest.

## Resultados

Cifras de `evidencia/busqueda_comparacion.json` (validación cruzada de 5 pliegues; entre paréntesis, desviación estándar muestral).

| Modelo | Exactitud | Malos detectados (recall) | Ajuste (s por pliegue) |
|---|---|---|---|
| Árbol por defecto | .690 (.013) | .480 (.038) | 0.015 |
| Árbol afinado (anidada) | .710 (.033) | .357 (.115) | ≈ 5 (incluye la búsqueda) |
| Random Forest | .765 (.020) | .417 (.012) | 0.197 |
| HistGradientBoosting | .766 (.011) | .510 (.035) | 0.264 |

Línea base «siempre bueno» = .700. El informe y la recomendación están en `informe/`.
