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
    # TODO 5 (en clase): from_pretrained del tokenizador y del modelo
    raise NotImplementedError("TODO 5: completar en clase")


def explicar(tokenizador, modelo, datos, prob):
    """Pide al modelo de lenguaje una explicación breve de la probabilidad `prob` para esta solicitud."""
    # TODO 6 (en clase): armar el mensaje, generar y decodificar
    raise NotImplementedError("TODO 6: completar en clase")


def recortar_a_oracion(texto):
    """Si el modelo se quedó sin espacio a mitad de frase, deja solo las oraciones completas."""
    if texto.endswith((".", "!", "?")):
        return texto
    corte = max(texto.rfind("."), texto.rfind("!"), texto.rfind("?"))                # último punto de cierre
    return texto[:corte + 1] if corte > 0 else texto
