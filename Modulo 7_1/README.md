# Demo Clase 7 · Aplicación híbrida: un modelo predictivo y un modelo de lenguaje

Un Random Forest (el de la Clase 6) predice la probabilidad de que un crédito sea malo. Un modelo de lenguaje
pequeño redacta la explicación. Una capa de verificación comprueba que el texto no afirme nada que el modelo no
sustente, y si falla, se muestra un texto de respaldo armado solo con datos. Esta es la versión **incompleta**: los bloques `TODO` se escriben en clase.

## Instalación

Requiere Python 3.10 a 3.12 (en Mac con chip Intel, Python 3.12). Con el entorno virtual activo:

```bash
pip install -r requirements.txt
python probar_modelo.py      # comprueba que el modelo de lenguaje descarga y responde
```

## Qué hay en cada archivo

| Archivo | Qué hace |
|---|---|
| `datos.py` | Lee German Credit y traduce una solicitud a datos legibles |
| `predictor.py` | El modelo predictivo (Random Forest) y la probabilidad de crédito malo |
| `red_neuronal.py` | Una red neuronal sencilla: capas y pesos |
| `explicador.py` | El modelo de lenguaje que redacta la explicación |
| `verificador.py` | Las verificaciones y el texto de respaldo |
| `main.py` | Ejecuta la aplicación completa sobre seis solicitudes |
| `tareas.py` | Comandos reutilizables: `evaluar`, `auditar` y `probar` |
| `hooks/pre-commit` y `instalar_hook.py` | La automatización: pruebas antes de cada commit |
| `tests/test_hibrido.py` | Pruebas automáticas |
| `verificar.py` | Comprueba un bloque: `python verificar.py <número de TODO>` |
| `verificar_extension.py` | Comprueba la estructura de la extensión: `python verificar_extension.py` |

## Cómo se completa

Cada `TODO n` marca un bloque que se escribe en clase. Para verificar cada paso:

```bash
python verificar.py 1     # cambia el número para cada bloque
python main.py            # cuando estén todos los bloques
pytest -v                 # con los TODO 10 y 11
```
La versión terminada está en `Demo_Hibrido_completo/`.

## La extensión (plugin)

Un plugin es una carpeta que empaqueta comandos y agentes para reutilizarlos en otro proyecto. Se arma en el paso 23 del instructivo y se comprueba con `python verificar_extension.py`. Con Claude Code se carga con `claude --plugin-dir extension` y sus comandos aparecen como `/auditoria-hibrida:auditar` y `/auditoria-hibrida:probar`.
