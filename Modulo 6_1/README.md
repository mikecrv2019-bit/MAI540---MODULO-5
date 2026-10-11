# Tarea 6.1 · Flujo de trabajo con agentes especializados (German Credit)

MAI 540 · Machine Learning · Atlantis University. Dataset: `datos/credit_g.csv`
(1,000 solicitudes, 20 variables, objetivo `clase`; `bad` = crédito malo).

## Flujo

```
Analista de datos ──► Ingeniero de modelos ──► Auditor
 resumen de datos      métricas (CV y 75/25)    reporte del auditor
```

| Rol | Definición | Entregable | Evidencia |
|---|---|---|---|
| Analista de datos | `.claude/agents/analista_datos.md` | resumen de datos + `src/datos.py` | `evidencia/01_analista_datos/` |
| Ingeniero de modelos | `.claude/agents/ingeniero_modelos.md` | métricas + `src/modelos.py`, `src/validacion.py` | `evidencia/02_ingeniero_modelos/` |
| Auditor | `.claude/agents/auditor.md` | reporte de auditoría | `evidencia/03_auditor/` |

## Reproducir desde cero

```bash
cd "Modulo 6_1"     # esta carpeta dentro del repositorio MAI540---MODULO-5
pip install -r requirements.txt
python src/reproducir.py
```

Semillas documentadas: validación cruzada `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`;
modelos con `random_state=42`; partición única 75/25 con semillas 0 a 29 (`random_state`).

## Resultados (generados desde `evidencia/02_ingeniero_modelos/metricas.json`)

| Modelo | Exactitud CV (M ± DE) | Malos detectados CV (M ± DE) | Exactitud 75/25, 30 semillas (mín–máx) |
|---|---|---|---|
| Árbol de decisión | .698 ± .019 | .530 ± .046 | .608–.720 |
| Random Forest | .759 ± .007 | .377 ± .019 | .712–.804 |

Línea base «siempre bueno» = .700. Detalle completo en `evidencia/02_ingeniero_modelos/metricas.md`.

## Entregables

- Informe APA: `informe/Informe_Tarea_6_1.docx` (se regenera con `python informe/generar_informe.py`).
- Evidencia por rol: `evidencia/01_analista_datos/`, `evidencia/02_ingeniero_modelos/`, `evidencia/03_auditor/`.
- Nota: el subagente auditor no pudo escribir su reporte por una restricción de la herramienta; `reporte_auditor.md`
  es la transcripción de su mensaje final (indicado en el propio archivo). `verificar.py` y su salida sí son del auditor.
