# Limitaciones y degradación

Responde las cinco preguntas de la guía de entrega. Las cifras salen de `evidencia/` y se pueden reproducir con los comandos del README.

## 1. ¿Para qué sirve?

Describir a cuál de tres perfiles químicos (`class_0`, `class_1`, `class_2`) se parece un lote de vino a partir de 13 mediciones de
laboratorio, con la probabilidad de cada perfil, para que un enólogo decida si necesita revisarlo. En validación cruzada acierta
0.981 ± 0.022 frente a 0.401 de la línea base.

## 2. ¿Para qué NO debe usarse, y por qué?

| No usar para… | Por qué |
|---|---|
| Asignar la línea de producto (entrada, revisión, premium) sin una persona | El modelo predice el `cultivar` de un archivo público de UCI. No hay datos de qué lote vende la empresa en cada línea; esa correspondencia no se ha definido ni validado. |
| Clasificar vinos de otras regiones, uvas o años, o medidos con otro método | Se entrenó con 178 muestras de tres cultivares de una sola fuente. Fuera de ese mundo el modelo extrapola: acierta menos y no lo sabe. |
| Confiar en un resultado con confianza menor a 80 % | Los 3 errores de los 178 lotes están en ese grupo: de 12 lotes con confianza baja, 3 fallan (25 %; IC 95 % de 9 % a 53 %). Con confianza ≥ 80 % no hubo errores en 166 lotes. |
| Sustituir el análisis de laboratorio o una decisión de calidad o seguridad | Solo hay 178 lotes y 3 errores observados: no alcanza para garantizar una tasa de error baja en producción. |
| Concluir que «el modelo es casi perfecto» | Este conjunto es famoso por ser fácil (casi cualquier modelo supera 0.9). La cifra mide el conjunto, no a los vinos de la empresa. |
| Decidir sobre personas | No usa ni contiene datos de personas. Si se agregaran variables sensibles (edad, sexo, estado civil de un cliente), servirían para auditar, no para decidir. |

## 3. Qué datos cambiarían con el tiempo

- **Método o instrumento de medición:** la prolina y el magnesio dependen del método de laboratorio; un instrumento nuevo o recalibrado corre sus valores.
- **Cosechas y proveedores:** el clima de cada año y un viñedo nuevo mueven las distribuciones de alcohol, intensidad de color o fenoles.
- **Mezcla de lotes:** si cambia la proporción de cada perfil que llega al laboratorio, cambian las probabilidades previas (hoy 33 %, 40 %, 27 %).
- **La relación entre variables y perfil:** un perfil nuevo que no existía en el entrenamiento. Es el cambio más difícil de ver.

## 4. Cómo se notaría

Lo que muestra la simulación (`evidencia/degradacion.md`, 100 repartos, supuestos y no mediciones reales):

| Cambio simulado | Exactitud | Lo detecta la alerta de… |
|---|---|---|
| Sin cambio | 0.983 | Falsas alarmas: 1 % (distribución) y 0 % (rango) |
| Prolina +25 % | 0.970 (−0.013) | Distribución en 21 % de los repartos; rango en 9 % |
| Prolina +50 % | 0.943 (−0.040) | Distribución en 100 %; rango en 49 % |
| Ruido de 0.5 desviaciones | 0.950 (−0.032) | Rango en 98 %; distribución solo en 6 % |
| Ruido de 1.0 desviaciones | 0.871 (−0.112) | Rango en 100 %; distribución en 18 % |

Qué enseña, y también sus límites:

1. **El modelo no avisa cuando se degrada.** Con ruido de una desviación pierde 11 puntos y sigue devolviendo probabilidades que parecen razonables.
2. **Ninguna alerta sola alcanza.** La de distribución ve el corrimiento de la media (otro método) y casi no ve el ruido; la de rango ve el ruido y apenas el corrimiento. La herramienta usa las dos.
3. **Una alerta no es una caída medida.** Con prolina +25 % la exactitud baja 1.3 puntos pero la alerta salta en 21 % de los repartos; con +10 % no salta casi nunca y también baja. La única señal definitiva es la exactitud con lotes **etiquetados**, que exige conocer la clase real.
4. **Los umbrales son de la simulación.** El 30 % de lotes fuera de rango se eligió porque, sin cambios, ~15 % de los lotes ya sale del rango (13 variables a la vez); no se calibró con datos de la empresa. Con menos de 20 lotes solo se mira el rango.
5. **Los avisos de confianza baja** se fijaron en 80 % mirando los mismos 3 errores (todos bajo 0.68) de los 178 lotes, que incluyen los 36 de la prueba final. La auditoría lo marcó como FALLA en V3.1 (`auditorias/AUDIT_REPORT_8_2.md`): ninguna cifra reportada depende del umbral, pero su capacidad real para atrapar errores futuros es probablemente menor que la observada.

## 5. Cuándo se revisa o se reentrena

| Disparador | Acción |
|---|---|
| Cambia el método, instrumento o laboratorio de medición | Reevaluar de inmediato con al menos 40 lotes etiquetados; reentrenar si baja la exactitud. |
| La exactitud con lotes nuevos etiquetados cae más de 0.05 respecto a 0.981 (menos de 0.931) | Reentrenar con los lotes nuevos y repetir validación cruzada, línea base y análisis de errores. |
| La alerta de deriva salta en dos archivos seguidos | Investigar la causa (método, proveedor, error de captura) antes de seguir usando las predicciones. |
| Se incorporan datos reales de la empresa o se define la correspondencia perfil → línea de producto | Reentrenar y revalidar: es otro problema, con otra variable objetivo. |
| Pasan 6 meses o una cosecha completa sin reevaluar | Revisión periódica aunque no haya alertas. |

El umbral de 0.05 se eligió porque con 45 lotes de evaluación la exactitud varía unos 0.02 de un reparto a otro; una caída de 0.05 son más de dos desviaciones. Los 6 meses y los 40 lotes son criterio del autor, sin base empírica propia.

## 6. Lo que no se pudo comprobar

- No hay lotes reales de la empresa: toda la degradación es simulada.
- Una sola fuente de datos: la generalización a otros laboratorios o años no se midió.
- Con 3 errores, ninguna comparación entre terciles de alcohol, prolina o magnesio es concluyente, y la Skill de auditoría marca como «no se puede determinar» la disparidad entre clases por tener menos de 20 casos por clase en la prueba final.
- La prueba de uso con una persona distinta del autor está pendiente de registrar (`revision/prueba_usuario.md`).
