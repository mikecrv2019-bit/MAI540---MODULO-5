# Prueba de instalación siguiendo solo el README

## 1. Clon limpio con entorno nuevo (hecha el 2026-10-22 por el autor con asistencia de Claude)

Esta NO sustituye la prueba con otra persona (sección 2): quien la hizo conoce el proyecto.

Pasos: clon del repositorio en una carpeta vacía, `python -m venv .venv`, `pip install -r requirements.txt`,
`python src/entrenar.py`, `python src/predecir.py --fila 0`, `pytest`. Resultado: las cifras salieron idénticas a las del
README (regresión logística 0.981 ± 0.022; prueba 0.972) y las pruebas pasaron, aunque el entorno limpio instaló versiones
más nuevas que el de desarrollo (pandas 3.1.0 frente a 2.3.3; scikit-learn 1.9.1 frente a 1.9.0).

Qué costó:

| Dónde | Qué pasó | Qué se hizo |
|---|---|---|
| `python -m venv .venv` | `WinError 267: The directory name is invalid` cuando la carpeta del clon tenía una ruta de más de 300 caracteres. | Se clonó en una ruta corta; se documentó en el README (sección Instalación). |
| `pip install` | Tardó 143 s. | Se avisa en el README: «unos 2 o 3 minutos». |
| `mcp dev` | `requirements.txt` instalaba `mcp` sin el comando. | Se cambió a `mcp[cli]` (comprobado: existe `mcp.exe`). |

## 2. Persona que no conoce el proyecto (PENDIENTE)

Pedirle a alguien que no haya visto el proyecto que siga solo el README, sin ayuda, y anotar aquí lo que le costó. Esta
sección se completa con sus palabras; no se rellena con suposiciones.

| Dato | Respuesta |
|---|---|
| Quién (nombre o rol) y sistema operativo | _pendiente_ |
| ¿Instaló sin ayuda? ¿Cuánto tardó? | _pendiente_ |
| ¿Qué paso del README no entendió o falló? | _pendiente_ |
| ¿Qué cambió en el README después? (commit) | _pendiente_ |
