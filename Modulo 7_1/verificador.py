"""Paso 4 · Verificar la capa generativa: que el texto no afirme nada que el modelo no sustente."""
import re


def _numeros(texto):
    """Todos los números que aparecen en un texto, como conjunto de floats."""
    return {float(n.replace(",", ".")) for n in re.findall(r"\d+(?:[.,]\d+)?", texto)}


def verificar_numeros(texto, datos, prob):
    """Devuelve una lista de problemas: números del texto que no vienen de los datos ni del modelo."""
    # TODO 7 (en clase): comparar los números del texto con los permitidos
    raise NotImplementedError("TODO 7: completar en clase")


def verificar_tono(texto, prob):
    """Devuelve una lista de problemas: el tono no coincide con la probabilidad, o hay afirmaciones absolutas."""
    # TODO 8 (en clase): reglas de coherencia con la probabilidad
    raise NotImplementedError("TODO 8: completar en clase")


def explicacion_segura(datos, prob):
    """Texto de respaldo, armado solo con datos y la probabilidad. No usa el modelo de lenguaje."""
    # TODO 9 (en clase): plantilla determinista de respaldo
    raise NotImplementedError("TODO 9: completar en clase")


def verificar_explicacion(texto, datos, prob):
    """Reúne todas las verificaciones. Lista vacía = el texto se puede mostrar."""
    return verificar_numeros(texto, datos, prob) + verificar_tono(texto, prob)
