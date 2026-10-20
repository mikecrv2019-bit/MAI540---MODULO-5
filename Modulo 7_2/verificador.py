"""Paso 4 · Verificar la capa generativa: que el texto no afirme nada que el modelo no sustente."""
import re


def _numeros(texto):
    """Todos los números que aparecen en un texto, como conjunto de floats."""
    return {float(n.replace(",", ".")) for n in re.findall(r"\d+(?:[.,]\d+)?", texto)}


def verificar_numeros(texto, datos, prob):
    """Devuelve una lista de problemas: números del texto que no vienen de los datos ni del modelo."""
    permitidos = _numeros(" ".join(str(v) for v in datos.values())) | _numeros(f"{prob:.0%}")   # datos + la probabilidad en %
    return [f"número no sustentado: {n:g}" for n in sorted(_numeros(texto) - permitidos)]      # lo que sobra es inventado


def verificar_tono(texto, prob):
    """Devuelve una lista de problemas: el tono no coincide con la probabilidad, o hay afirmaciones absolutas."""
    t = texto.lower()                                        # minúsculas para comparar
    problemas = []
    if prob < 0.30 and re.search(r"\b(alto|elevado|grave)\b", t):       # probabilidad baja pero dice «alto»
        problemas.append("dice que el riesgo es alto, pero la probabilidad es baja")
    if prob > 0.60 and re.search(r"\b(bajo|mínimo|minimo)\b", t):       # probabilidad alta pero dice «bajo»
        problemas.append("dice que el riesgo es bajo, pero la probabilidad es alta")
    for absoluta in ("garantiza", "garantizado", "sin riesgo", "seguro que", "imposible", "nunca", "siempre", "100%"):
        if absoluta in t:                                    # certezas que un modelo de probabilidades no da
            problemas.append(f"afirmación absoluta: '{absoluta}'")
    return problemas


def explicacion_segura(datos, prob):
    """Texto de respaldo, armado solo con datos y la probabilidad. No usa el modelo de lenguaje."""
    nivel = "bajo" if prob < 0.30 else ("medio" if prob <= 0.60 else "alto")   # mismos umbrales que verificar_tono
    detalle = ", ".join(f"{k}: {v}" for k, v in datos.items())                 # los datos de la solicitud
    return f"El modelo estima una probabilidad de {prob:.0%} de que el crédito sea malo (riesgo {nivel}). Datos: {detalle}."


def verificar_explicacion(texto, datos, prob):
    """Reúne todas las verificaciones. Lista vacía = el texto se puede mostrar."""
    return verificar_numeros(texto, datos, prob) + verificar_tono(texto, prob)
