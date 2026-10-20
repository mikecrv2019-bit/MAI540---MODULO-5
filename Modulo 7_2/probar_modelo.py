"""Comprueba que el modelo de lenguaje está instalado y responde.

Uso:  python probar_modelo.py
La primera vez descarga el modelo (unos 1 GB) y puede tardar unos minutos.
"""
import time
import warnings

warnings.filterwarnings("ignore")                                  # oculta avisos que no afectan el resultado

try:
    import torch                                                   # torch: la librería que ejecuta el modelo
    from transformers import AutoModelForCausalLM, AutoTokenizer   # transformers: carga el modelo y su tokenizador
    from transformers.utils import logging
except ImportError:
    raise SystemExit("Falta instalar las dependencias. Con (.venv) activo ejecuta:  pip install -r requirements.txt")

logging.set_verbosity_error()
MODELO = "Qwen/Qwen2.5-0.5B-Instruct"                              # modelo pequeño (0.5 mil millones de parámetros)

inicio = time.time()
tokenizador = AutoTokenizer.from_pretrained(MODELO)                # convierte texto a números y de vuelta
modelo = AutoModelForCausalLM.from_pretrained(MODELO, torch_dtype=torch.float32).eval()
print(f"Modelo cargado en {time.time() - inicio:.1f} s")

mensajes = [
    {"role": "system", "content": "Respondes en español, en una sola frase corta."},
    {"role": "user", "content": "¿Qué es un crédito bancario?"},
]
entrada = tokenizador(tokenizador.apply_chat_template(mensajes, tokenize=False, add_generation_prompt=True), return_tensors="pt")
inicio = time.time()
with torch.no_grad():                                              # no_grad: solo generamos, no entrenamos
    salida = modelo.generate(**entrada, max_new_tokens=40, do_sample=False, temperature=None, top_p=None, top_k=None)
texto = tokenizador.decode(salida[0][entrada["input_ids"].shape[1]:], skip_special_tokens=True).strip()
print(f"Respuesta ({time.time() - inicio:.1f} s): {texto}")
print("LISTO: el modelo funciona." if texto else "El modelo no devolvió texto.")
