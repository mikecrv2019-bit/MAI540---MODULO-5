# Prueba de uso con una persona distinta del autor (Tarea 8.2)

La Tarea 8.2 pide que una persona distinta del autor use la demostración y que se anote qué le costó y qué se cambió. **Esta prueba
NO se ha hecho todavía**: la sección 2 se completa con las palabras de esa persona y no se rellena con suposiciones.

## 1. Verificación previa hecha por el autor (2026-10-23, con asistencia de Claude)

No sustituye a la sección 2: quien la hizo conoce el proyecto.

- `pip install -r requirements.txt` en el entorno de desarrollo, `pytest -v`: 40 pruebas en verde (`evidencia/pytest_v_final.txt`).
- `python app_gradio.py`: la pantalla abre en `http://127.0.0.1:7860`; el botón «Lote ambiguo (el 83)» + «Clasificar lote» muestra
  `class_1` con 66 % y el aviso de confianza baja; «Lote típico class_0» da 100 % sin aviso.
- La pestaña de archivo, con `datos/wine.csv`: 178 lotes, 4 con confianza baja, exactitud 100 % (son los lotes de entrenamiento), sin deriva.
- `python src/predecir.py --fila 83` devuelve el mismo resultado desde la línea de comandos.
- Hallazgo de esta verificación: `requirements.txt` no incluía `gradio` (la app no habría abierto en una instalación limpia) y la prueba
  de la pantalla se omitía en silencio por la misma razón. Corregido: `gradio>=5.0` y `scipy>=1.11` agregados; ahora no hay pruebas omitidas.
- Pendiente de comprobar: una **instalación limpia** (clon nuevo + entorno nuevo) siguiendo el README; solo se probó en el entorno de desarrollo.

## 2. Persona que no conoce el proyecto (PENDIENTE)

**Qué pedirle (texto para enviarle):**

> Necesito que pruebes una herramienta, sin que yo te ayude. Abre el archivo README.md de la carpeta `Modulo 8_2`, sigue las secciones
> «Instalación» y «Cómo ejecutar» (Opción A) y haz lo que dice el README. Al final intenta contestar: ¿a qué perfil se parece el
> lote ambiguo y por qué la herramienta dice que no hay que fiarse mucho? Anota cuánto tardaste, dónde te trabaste y qué no entendiste.
> Si te toca escribirme para pedir ayuda, apunta qué preguntaste.

**Qué observar (sin intervenir):** si instala sin ayuda; cuánto tarda; si entiende qué significa «perfil químico» y «confianza baja»;
si nota por sí misma el aviso de limitaciones; si sabe qué hacer con una confianza menor a 80 %.

| Dato | Respuesta |
|---|---|
| Quién (nombre o rol) y sistema operativo | _pendiente_ |
| ¿Instaló sin ayuda? ¿Cuánto tardó (instalación y primera ejecución)? | _pendiente_ |
| ¿Qué paso del README no entendió o falló? | _pendiente_ |
| ¿Entendió el resultado del lote ambiguo? ¿Con qué palabras lo explicó? | _pendiente_ |
| ¿Qué le costó de la pantalla (etiquetas, avisos, el archivo CSV)? | _pendiente_ |
| ¿Qué cambió el autor después? (commit) | _pendiente_ |

## 3. Dónde se espera que tropiece (hipótesis, no resultados)

Estas son suposiciones del autor a partir de la prueba de instalación de la Tarea 8.1 (`Modulo 8_1/revision/prueba_instalacion.md`);
se confirman o se descartan con la sección 2.

- En Windows, una ruta de carpeta larga rompe `python -m venv` (`WinError 267`); el README lo advierte.
- La instalación con Gradio tarda unos minutos y puede parecer colgada.
- La primera ejecución entrena el modelo y no imprime nada durante unos segundos antes de la dirección.
- Quien no sabe de química puede no saber qué hacer con 13 campos: por eso el formulario arranca con valores típicos y hay cuatro botones de ejemplo.
