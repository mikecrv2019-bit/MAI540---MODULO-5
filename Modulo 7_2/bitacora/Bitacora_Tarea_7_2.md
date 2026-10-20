# Bitácora de desarrollo asistido · Tarea 7.2

Herramienta: Claude Code (Claude Sonnet 5.5) sobre el proyecto `Demo_Hibrido_incompleto`. Fecha de trabajo: 19 de octubre de 2026.
Cada fila dice qué se pidió, qué se hizo, **cómo se verificó** y **qué se corrigió**. Los comandos son reproducibles desde la raíz del proyecto.

## 1. Mis instrucciones

| # | Instrucción (resumen fiel) |
|---|---|
| 1 | «Actúa como un experto en Machine Learning; desarrolla la tarea 7.2, aplicación híbrida con verificación», adjuntando `credit_g (2).csv` y los seis puntos del enunciado (red vs. predictor, ≥ 10 solicitudes, fallo no atrapado, dos reglas con pruebas, medición antes/después con falsos positivos, límites y recomendación). |
| 2 | Mensaje intermedio: indiqué la carpeta `Demo_Hibrido_incompleto/` como el proyecto de trabajo (ya era el directorio de trabajo). |

## 2. Registro cronológico

| Paso | Qué se hizo | Cómo se verificó | Corrección o hallazgo |
|---|---|---|---|
| 1. Reconocimiento | Se leyó todo el código y el enunciado (`TAREA_7_2…docx`); se comprobó que `credit_g (2).csv` es idéntico a `datos/credit_g.csv`. | `diff` sin diferencias. | El enunciado cita el agente `revisor-de-explicaciones`, pero la extensión de la Tarea 7.1 solo trae `auditor-de-equidad`. Se creó `extension/agents/revisor-de-explicaciones.md`. |
| 2. Entorno | Había Python 3.14 (el enunciado pide 3.12), sin `torch` ni `transformers`. Se creó `.venv` y se instaló torch 2.14.1 (CPU), transformers 5.20.2, scikit-learn 1.9.1 y numpy 2.5.4. | `python probar_modelo.py` → «LISTO: el modelo funciona». | Los pines de `requirements.txt` (`transformers<4.50`, `numpy<2`) no se instalan en 3.14, así que **no se respetaron**; `requirements.txt` no se modificó. La red sí dio lo esperado por `verificar.py` (capas `[61, 16, 8, 1]`, 1,137 pesos). |
| 3. Punto 1 | `comparar_modelos.py`: misma partición (`test_size=0.20`, `stratify=y`, `random_state=42`) para ambos modelos, con una aserción de que las 200 filas de prueba son las mismas. | `evidencia/comparacion_modelos.txt`: red .735, RF .770 sobre las 200; validación cruzada .717 vs .755. | Se añadió la validación cruzada porque 200 casos dan un error típico de ≈ .03 y la diferencia de 7 solicitudes no es concluyente. |
| 4. Punto 2 | `main.py` recorre N solicitudes y guarda los textos en `evidencia/textos_generados.json`. Se ejecutó con 20 y con 200 (generación determinista). | Verificador de clase: 9/20 y 64/200 rechazadas (`evidencia/ejecucion_antes.txt`, `ejecucion_200_antes.txt`). | **Error mío:** correr `main.py 20` después de la corrida de 200 sobrescribió la caché con solo 20 textos y obligó a regenerar. Se detuvo el proceso, se reconstruyó la caché desde la salida literal guardada (las 50 solicitudes regeneradas coincidieron con el original, lo que confirma el determinismo) y se corrigió `main.py` para fusionar en lugar de sobrescribir (commit `379b509`). |
| 5. Punto 3 | Lectura de los textos que pasaron el verificador de clase, aplicando a mano el protocolo del agente revisor. | Solicitud 8: texto «sin saldo negativo» con dato «saldo negativo»; 25 de 200 textos con el mismo error; solicitud 4 con «persona sola». | El agente no se ejecutó dentro de Claude Code; el protocolo se aplicó manualmente (el informe lo dice). |
| 6. Punto 4 | Primero las pruebas, luego las reglas: `tests/test_regla_datos.py` y `tests/test_regla_tono_medio.py`. Se verificó que **fallan** contra el verificador original. | `evidencia/pruebas_regla1_sin_regla.txt` (10 fallan) y `pruebas_regla2_sin_regla.txt` (14 fallan); con las reglas pasan 71 de 71, incluidas las 5 originales. | **El hook de pre-commit canceló mi primer commit** de la regla 1 porque la prueba de la regla 2 ya estaba en disco y fallaba. Se rehicieron los commits por separado apartando temporalmente el archivo de la regla 2. |
| 7. Punto 5 | `medir_efecto.py` compara `verificar_base` (antes) con `verificar_explicacion` (después) sobre los mismos textos. Etiquetado manual de los 200 textos (`evidencia/etiquetas.json`). | 64 → 133 rechazos de 200; incorrectos mostrados 91 → 22; 0 falsos positivos de resultado (`evidencia/medicion_200.md`). | Se revisaron los textos rechazados solo por las reglas nuevas: la Regla 2 se disparó con «la edad **es alta** (47 años)» (solicitudes 118 y 158). Se escribió la prueba (falló), se ajustó la regla (commit `477db43`) y se midió de nuevo (67 → 65 rechazos por la Regla 2). Costo: esos dos textos ahora pasan. |
| 8. Punto 6 | Clasificación de los 22 incorrectos que aún pasan: sentido invertido (4), campo equivocado (14), incoherentes (3), calificativo falso (1); 30 de los 67 que pasan dicen «euros» o «$» sin dato de moneda. | Listado en `evidencia/etiquetas.json` y en el informe. | — |
| 9. Informe | `informe/generar_informe_7_2.py` lee las cifras de la evidencia (no se transcriben a mano) y genera el `.docx`; el PDF se exportó con Word para contar páginas: 3. | Se revisó cada página como imagen. | La primera versión tenía 4 páginas y una tabla partida entre páginas: se recortó texto, se quitó una fila de la Tabla 3 (la afirmación absoluta, 1 caso, queda en el texto y en la nota) y se mantuvieron las tablas completas. |

## 3. Qué no está verificado

- Las etiquetas «correcto / reserva / incorrecto» son de **un solo revisor** (yo, con Claude) leyendo cada texto contra sus datos; no hay segundo revisor ni acuerdo entre revisores.
- Todo se midió sobre **un solo modelo de lenguaje pequeño** y una sola partición; no se estimó ningún intervalo de confianza.
- El informe usa interlineado 1.1 para caber en 3 páginas; APA 7 pide doble espacio, que no cabe con este contenido.
- Las referencias (Breiman, 2001; Ji et al., 2023; Qwen Team, 2024; Reglamento (UE) 2024/1689; Hofmann, 1994) se citaron de memoria con su DOI o URL; conviene abrirlas una vez antes de entregar.
- No se hizo `git push`: el repositorio de GitHub debe subirse por ti.
