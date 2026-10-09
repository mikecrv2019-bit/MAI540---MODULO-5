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
pip install -r requirements.txt
python src/reproducir.py
```

Semillas documentadas: validación cruzada `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)`;
modelos con `random_state=42`; partición única 75/25 con semillas 0 a 29 (`random_state`).
