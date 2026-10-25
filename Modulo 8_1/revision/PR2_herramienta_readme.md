# Pull request 2: herramienta de uso (CLI y servidor MCP), README y auditoría final

Rama `feat/herramienta-readme` → `main` (se apoya en el PR 1: debe integrarse después de él).

## Qué cambia

Agrega `src/predecir.py` (clasifica un lote con validación de entradas y advertencia de rango), `src/mcp_server.py` con las
tools `clasificar_lote` y `resumen_validacion`, `verificar_servidor.py`, el README con la plantilla del Módulo 8, la
segunda auditoría de la Skill y 5 pruebas nuevas.

## Por qué

El modelo validado del PR 1 solo es útil si otra persona puede instalarlo, ejecutarlo y entender sus límites.

## Cómo se probó

- [x] `pytest -v` pasa: 21 pruebas (`evidencia/pytest_v_final.txt`)
- [x] Ejecuté la herramienta: `python src/predecir.py --fila 0` → `class_0` con 0.9998; y `verificar_servidor.py` por stdio (`evidencia/verificacion_servidor.log`)
- [x] Instalación en un clon limpio con un entorno virtual nuevo, siguiendo solo el README (`revision/prueba_instalacion.md`)

## Lista de revisión

- [x] El cambio es pequeño y tiene un solo propósito: poner el modelo en manos de un usuario
- [x] El README está al día
- [x] No hay datos personales, claves ni información confidencial (el hook busca claves en cada commit; ningún `.env` ni clave en el árbol)
- [x] Las pruebas nuevas cubren el cambio
- [x] Los mensajes de commit explican qué hizo cada uno

---

## Revisión

**Revisor:** Skill `auditoria-modelos` v2.0 (informe `auditorias/AUDIT_REPORT_2_final.md`, auditoría completa e independiente
de la primera) y revisión de código asistida por Claude. Pendiente: revisión humana (docente o compañero), que se anota aquí.

**Qué revisó:** los 8 módulos de `src/` que entrenan, evalúan o usan el modelo, `evidencia/resultados.json` y el README
como declaración del proyecto (costos, variables, momento en que se conocen).

**Hallazgos y comentarios (con archivo y línea, sobre el estado previo a las correcciones):**

1. `requirements.txt:6` — `mcp>=2.0` no instala el comando `mcp`, pero `README.md:141` pide `mcp dev src/mcp_server.py`.
2. `src/mcp_server.py:32` — ante un lote inválido el cliente solo recibe `Error executing tool` (visible en
   `evidencia/verificacion_servidor.log`); no sabe qué variable falta.
3. `README.md:155` y `README.md:184` — mencionan `evidencia/pytest_v_final.txt` y `BITACORA.md`, que aún no existían.
4. `README.md:96` — sin aviso de que `python -m venv` falla en Windows con rutas largas (ocurrió en la instalación limpia).
5. V1.5 (NO SE PUEDE DETERMINAR) — multiclase sin costos distintos; el README lo declara pero la Skill no puede dar PASA.
6. V4.2 (NO SE PUEDE DETERMINAR) — 12, 14 y 10 casos por clase en la prueba (< 20).

**Cambios que se pidieron y cómo se resolvieron:**

| # | Resolución | Commit |
|---|---|---|
| 1 | `mcp[cli]>=2.0`; el comando existe en el entorno limpio (`mcp.exe`). | `fix(requirements)` |
| 2 | La tool devuelve `{"error": motivo}`; prueba `test_la_tool_mcp_devuelve_el_motivo_cuando_el_lote_es_invalido`. | `fix(review): la tool clasificar_lote ...` |
| 3 | Se crean la salida final de `pytest -v` y la bitácora. | `docs(evidencia)` y `docs(bitacora)` |
| 4 | Nota de `WinError 267` y del tiempo de instalación (≈ 2.4 min). | `docs(readme): nota de ruta larga ...` |
| 5 | Sin corrección: no hay costos de la empresa. Queda declarado en `README.md:15-18` y como acción abierta en la auditoría. | — |
| 6 | Sin corrección posible con 178 lotes; explicado en `README.md:165-166` y evidencia complementaria (brecha máxima fuera de pliegue 0.032 ≤ 0.10). | — |

**Decisión:** cambios solicitados → resueltos. Aprobado para integrar tras `pytest -v` en verde (21 pruebas).
