# Reflexión: cómo evolucionó mi criterio técnico en las ocho semanas

> **Borrador para el estudiante.** Está armado con la evidencia del repositorio (Módulos 5 a 8), no con mi memoria. Léalo, cambie lo que no
> sea cierto de cómo trabajó usted y borre este aviso antes de entregar.

**Al principio** (Módulo 5), un resultado bueno era uno que corría. Construí un servidor MCP con PCA y K-Means, lo probé con el
Inspector y di por buena la segmentación con una sola cifra, la silueta de 0.2849. No tenía una línea base ni sabía cuánto variaba esa cifra,
y no me preguntaba con qué datos se había decidido nada. En el Módulo 6 aprendí a pedir media y desviación de una validación cruzada, a
reproducir la cifra de la entrega anterior antes de cambiar nada, y a que una auditoría revise lo que yo no veo.

**Ahora** (Módulo 8), antes de preguntar cuánto acierta el modelo pregunto contra qué se compara (la línea base acierta 0.401, el modelo 0.981),
con qué datos se tomó cada decisión (la prueba final se mide una sola vez), en qué grupos falla (3 errores en 178 lotes, todos con confianza
menor a 0.68) y qué pasa cuando el mundo cambia (con ruido de una desviación la exactitud cae a 0.871 y el modelo no avisa). También cambió
cómo uso al asistente: ya no le pido «hazlo», le pido que lea antes de escribir, que consulte lo ambiguo, que no suba nada sin mi orden, y
yo compruebo lo que afirma. En esta tarea, por ejemplo, comprobé que la app realmente abriera y que el README no prometiera lo que la
pantalla no hacía, y eso destapó que `requirements.txt` no traía Gradio y que una prueba se omitía en silencio.

**Una decisión que habría tomado distinto.** Fijé el umbral de «confianza baja» en 80 % mirando los errores de los 178 lotes, que
incluyen los 36 de la prueba final. Parecía razonable porque no cambiaba ninguna métrica reportada, pero la auditoría lo marcó como fuga (V3.1):
el umbral «captura» los 3 errores precisamente porque se eligió con ellos. Lo correcto habría sido fijarlo con los 142 lotes de entrenamiento y
contar cuántos errores de la prueba atrapa. No fue la primera vez: en la Tarea 8.1 el escalador de K-Means se ajustó con las 178 filas
y también lo encontró la Skill, no yo. Lo que cambió no es que ya no cometa esos errores, sino que ahora sé nombrarlos, tengo una herramienta
que los busca y los declaro en las limitaciones en vez de esconderlos. Lo que todavía me falta es detectarlos antes de que los revise otro:
antes de usar «todos los datos» para decidir algo, preguntarme si algún dato de prueba entró en la decisión.
