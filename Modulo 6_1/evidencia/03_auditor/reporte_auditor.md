# Reporte del auditor · Rol 3

> **Nota de procedencia.** Este reporte lo redactó el subagente Auditor como mensaje final. Su herramienta de
> escritura se lo impidió («Subagents should return findings as text, not write report files»), y el auditor no
> lo eludió. El orquestador lo transcribió aquí sin cambiar su contenido. Lo que sí escribió el auditor
> directamente: `verificar.py` y `verificacion_salida.txt` (el orquestador volvió a ejecutar el script: salida idéntica).

## Veredicto: APROBADO CON OBSERVACIONES

No hay errores de método ni de cifras, y no hay fuga de información. `verificar.py`: **55/55 verificaciones OK, 0 fallos**.

## Verificaciones (código propio; solo se importó `src/modelos.py` para inspeccionar los Pipeline reales)

| # | Verificación | Resultado | Evidencia |
|---|---|---|---|
| 1 | Resumen de datos vs CSV | OK | Forma 1000×20; good 700 / bad 300; 0 faltantes (0 celdas vacías en el CSV crudo); 0 duplicados; 13 categóricas y 7 numéricas (int64); cardinalidades, conteos, tasa de bad y estadísticos coinciden; los `none` literales se conservan como categoría, no como NaN. |
| 2 | Codificación dentro del Pipeline, sin fuga | OK | `Pipeline[ColumnTransformer(OrdinalEncoder en 13 cat, passthrough en 7 num), modelo]`, sin ajustar antes de validar. En los 5 pliegues el `categories_` del encoder coincide con las categorías del entrenamiento (800 filas). Prueba de comportamiento: sin `retraining` en el entrenamiento, el test se codifica −1; un ajuste global sí la incluiría. |
| 3 | CV estratificada de 5 pliegues con semilla fija; clase positiva correcta | OK | `StratifiedKFold(5, shuffle=True, random_state=42)`: test disjuntos, 60 bad de 200 por pliegue. El recall usa `bad` como positiva: con `good` como positiva saldría 0.77 (árbol) y 0.92 (RF), así que no hay inversión de clase. |
| 4 | Cifras de `metricas.json` | OK | Reproducidas exactamente por pliegue; media y desviación (ddof=1) con diferencia < 1e-12. Árbol: exactitud 0.6980 ± 0.0189, recall bad 0.5300 ± 0.0462. RF: exactitud 0.7590 ± 0.0065, recall bad 0.3767 ± 0.0190. Línea base 0.70: árbol −0.20 pp, RF +5.90 pp. |
| 5 | Partición única, ≥10 semillas, diferencia vs CV | OK | 30 semillas (0..29) y subconjunto 0..9; los 60 pares (exactitud, recall) coinciden exactamente. Árbol, exactitud: −1.72 pp de media, rango [−9.00, +2.20]. RF, exactitud: −0.74 pp de media, rango [−4.70, +4.50]. |
| 6 | Afirmaciones del ingeniero | OK | `metricas.md` coincide con `metricas.json`. `ejecutar_ingeniero.py` regenerado en una copia fuera del repo: salida byte a byte idéntica. |

## Hallazgos

Ninguno de severidad que exija corrección. Observaciones:

| Severidad | Rol | Observación |
|---|---|---|
| Informativa | Ingeniero | La diferencia partición única vs CV se mide contra una sola CV con semilla 42. La dispersión entre particiones (desv. de exactitud 0.023) es mayor que entre pliegues (0.019 árbol, 0.0065 RF), y el árbol llega a −9 pp. Está bien reportado; la narrativa final no debe dar la media de 30 particiones como «la» diferencia. |
| Informativa | Ingeniero | El árbol no supera la línea base (0.698 vs 0.70). El RF sube la exactitud pero detecta solo 37.7 % de los créditos malos (el árbol, 53.0 %). `metricas.md` lo reporta con honestidad; hay que mantenerlo en la redacción final. |
| Baja | Analista | `resumen_datos.*` recomienda escalar y aplicar logaritmos a las numéricas. No cambia nada para árbol/RF y el ingeniero no lo aplicó. |
| Baja | Ingeniero | `OrdinalEncoder` impone un orden arbitrario a categóricas nominales. Es aceptable para árboles y es lo que pide la tarea; se puede mencionar en la memoria. |

## Alcance y límites de la auditoría

- El uso de `clone` / `scoring='recall'` / `pos_label=1` se comprobó leyendo el código; la corrección numérica se probó aparte con el recall recalculado a mano.
- En RF no se pudo comprobar las filas de entrenamiento desde el objeto ajustado; sí que el `categories_` coincide en los 5 pliegues.

## Script de verificación

`evidencia/03_auditor/verificar.py` → salida en `evidencia/03_auditor/verificacion_salida.txt`.
