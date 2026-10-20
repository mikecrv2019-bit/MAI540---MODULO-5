"""Paso 3 · El componente generativo: un modelo de lenguaje pequeño que redacta la explicación."""
import warnings

import torch                                                    # torch: ejecuta el modelo
from transformers import AutoModelForCausalLM, AutoTokenizer    # carga el modelo y su tokenizador
from transformers.utils import logging

warnings.filterwarnings("ignore")                               # oculta avisos que no afectan el resultado
logging.set_verbosity_error()

MODELO = "Qwen/Qwen2.5-0.5B-Instruct"                           # modelo pequeño (0.5 mil millones de parámetros)
SISTEMA = ("Eres un asistente de un banco. Explicas en español, en máximo dos frases, el resultado de un modelo de "
           "riesgo de crédito. Usa solo los datos que te dan y no inventes nada.")


def cargar_modelo_lenguaje():
    """Descarga (la primera vez) y carga el modelo de lenguaje. Devuelve (tokenizador, modelo)."""
    tokenizador = AutoTokenizer.from_pretrained(MODELO)                                           # texto ↔ números
    modelo = AutoModelForCausalLM.from_pretrained(MODELO, torch_dtype=torch.float32).eval()       # .eval(): solo generamos
    return tokenizador, modelo


def explicar(tokenizador, modelo, datos, prob):
    """Pide al modelo de lenguaje una explicación breve de la probabilidad `prob` para esta solicitud."""
    detalle = ", ".join(f"{k}: {v}" for k, v in datos.items())            # los datos como una línea de texto
    mensajes = [
        {"role": "system", "content": SISTEMA},                           # las reglas del asistente
        {"role": "user", "content": f"Datos: {detalle}. Probabilidad de crédito malo: {prob:.0%}. Explica."},
    ]
    texto = tokenizador.apply_chat_template(mensajes, tokenize=False, add_generation_prompt=True)   # formato de chat
    entrada = tokenizador(texto, return_tensors="pt")                     # texto → tensores
    with torch.no_grad():                                                 # no entrenamos: solo generamos
        salida = modelo.generate(**entrada, max_new_tokens=70, do_sample=False, temperature=None, top_p=None, top_k=None)
    nuevos = salida[0][entrada["input_ids"].shape[1]:]                    # solo lo que generó (no el mensaje)
    return tokenizador.decode(nuevos, skip_special_tokens=True).strip()   # tensores → texto


def recortar_a_oracion(texto):
    """Si el modelo se quedó sin espacio a mitad de frase, deja solo las oraciones completas."""
    if texto.endswith((".", "!", "?")):
        return texto
    corte = max(texto.rfind("."), texto.rfind("!"), texto.rfind("?"))                # último punto de cierre
    return texto[:corte + 1] if corte > 0 else texto
