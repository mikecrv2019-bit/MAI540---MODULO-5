# Pull request 1: modelo validado con validación cruzada, línea base y criterio de selección

Rama `feat/modelo-validado` → `main`. (Texto del PR según `plantilla_pull_request.md` del Módulo 8.)

## Qué cambia

Agrega el flujo de modelado del capstone en `Capstone_Dilitio_Wine/`: carga y validación de datos, línea base y cuatro
modelos en `Pipeline`, validación cruzada 5×3 con media y desviación, criterio explícito de selección, una sola medición en
la prueba final, análisis de errores por categoría y K-Means exploratorio, más 16 pruebas, el hook `pre-commit` y la Skill
de auditoría.

## Por qué

La propuesta del Módulo 5 pide un modelo defendible y no solo un número: validado con CV frente a una línea base sencilla
y con una regla de elección escrita antes de mirar la prueba.

## Cómo se probó

- [x] `pytest -v` pasa: 16 pruebas (salida completa en `evidencia/pytest_v_PR1.txt`)
- [x] Ejecuté la herramienta: `python src/entrenar.py` → `evidencia/resultados.md` y `evidencia/salida_entrenar.txt`
- [x] Salida del hook en cada commit (aceptado y cancelado): `evidencia/hook_commit_aceptado.txt`, `evidencia/hook_commit_cancelado.txt`

Resultado: F1 macro CV (media ± desv.) línea base 0.191 ± 0.004; regresión logística 0.981 ± 0.022 (elegida); Random Forest
0.981 ± 0.026; boosting 0.959 ± 0.033; árbol 0.921 ± 0.045. Prueba final del elegido: exactitud 0.972 (35/36).

## Lista de revisión

- [x] El cambio es pequeño y tiene un solo propósito: modelado y su validación (17 commits atómicos al abrir el PR)
- [ ] El README está al día → se escribe en el PR 2 (`feat/herramienta-readme`)
- [x] No hay datos personales, claves ni información confidencial (datos químicos públicos; el hook busca claves en cada commit)
- [x] Las pruebas nuevas cubren el cambio
- [x] Los mensajes de commit explican qué hizo cada uno

---

## Revisión

**Revisor:** Skill `auditoria-modelos` v2.0 (informe `auditorias/AUDIT_REPORT_1_antes_de_PR.md`) y revisión de código asistida
por Claude sobre el diff de la rama. Pendiente: revisión humana (docente o compañero), que se anota en este mismo archivo.

**Qué revisó:** los 7 módulos de `src/` y `evidencia/resultados.json` con los 15 subcriterios de la Skill (métricas,
partición, fuga, subgrupos, datos de entrada, variables) y una lectura línea por línea de los cambios.

**Hallazgos y comentarios (con archivo y línea, sobre el estado previo a las correcciones):**

1. `src/segmentacion.py:28` (V2.1, FALLA, alta) — `Xe = StandardScaler().fit_transform(X)`: el escalador del K-Means se
   ajusta con las 178 filas, incluida la prueba final.
2. `src/entrenar.py:55` (V3.1, FALLA, alta) — `"segmentacion_kmeans": segmentar(X, y)` pasa todo `X`; debe recibir la
   partición de entrenamiento.
3. `src/validacion.py:47` (revisión de código, media) — `if i < N_PLIEGUES` supone que el `cv` tiene 5 pliegues por
   repetición; con otro `cv` (p. ej. 10 pliegues) quedarían filas en `None` y el análisis de errores saldría falso sin avisar.
4. `src/seleccion.py:30` (revisión de código, baja) — `COMPLEJIDAD.index(n)` lanza un `ValueError` poco claro si se agrega
   un modelo nuevo y se olvida registrarlo.
5. `src/entrenar.py:62` (revisión de código, baja) — el modelo final se ajusta con los 178 lotes; debe documentarse que la
   cifra de la prueba corresponde al modelo ajustado solo con entrenamiento.
6. V1.5 (NO SE PUEDE DETERMINAR, media) — multiclase sin costos declarados; falta un `README.md` que lo diga.
7. V4.2 (NO SE PUEDE DETERMINAR, media) — la prueba tiene 12, 14 y 10 casos por clase (< 20).

**Cambios que se pidieron y cómo se resolvieron:**

| # | Resolución | Commit |
|---|---|---|
| 1 y 2 | `segmentar(X_tr, y_tr, X_te, y_te)` ajusta escalador y K-Means solo con entrenamiento; la prueba solo usa `predict` (ARI en prueba 0.909). La silueta pasó a 0.2875 ≥ 0.2849, ahora sin tolerancia. La prueba `test_kmeans_cumple_silueta_del_piloto_y_es_estable` verifica `ajustado_con < 178`. | `fix(audit V2.1/V3.1)` |
| 3 | `evaluar_cv` lanza `ValueError("... no cubre todas las filas ...")`; prueba `test_cv_que_no_cubre_todas_las_filas_falla_con_mensaje_claro`. | `fix(review): evaluar_cv ...` |
| 4 | `elegir_modelo` valida los nombres antes de ordenar; prueba `test_modelo_desconocido_da_error_claro`. | `fix(review): elegir_modelo ...` |
| 5 | Se documenta en el README (PR 2, sección «Cómo funciona»). | PR 2 |
| 6 | Se declara en el README (PR 2, sección «Problema»). | PR 2 |
| 7 | Sin corrección posible: con 36 filas de prueba ninguna clase llega a 20 casos. Se reporta la comparación con las predicciones fuera de pliegue (n = 47, 57, 38; brecha máxima 0.032 ≤ 0.10) y se explica en el README. | PR 2 |

**Decisión:** cambios solicitados → resueltos en la rama (los puntos 5–7 pasan al PR 2). Aprobado para integrar tras
`pytest -v` en verde (16 pruebas).
