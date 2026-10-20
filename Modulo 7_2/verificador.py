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


# ---- Regla nueva 1 · el texto no puede contradecir los datos de la solicitud --------------------------------------
_NIEGA_SALDO_NEG = r"\b(?:sin|no|ni)\s+(?:\w+\s+)?saldo\s+negativo|saldo\s+no\s+(?:es\s+)?negativo|saldo\s+positivo"
_CUENTA = {            # lo que el texto puede afirmar de la cuenta corriente -> patrón que lo detecta
    "saldo negativo": r"saldo\s+(?:es\s+)?negativo|saldo\s+en\s+rojo|sobregir\w+",
    "saldo entre 0 y 200": r"saldo\s+(?:\w+\s+){0,2}entre\s+0\s+y\s+200",
    "saldo de 200 o más": r"200\s+o\s+m[aá]s",
    "sin cuenta corriente": r"\bsin\s+cuenta\b",
}
_VIVIENDA = {           # lo que el texto puede afirmar de la vivienda -> patrón que lo detecta
    "alquilada": r"\balquil\w*|\barrend\w*",
    "propia": r"\b(?:vivienda|casa|hogar|inmueble)\s+(?:\w+\s+){0,2}propia\b|\bpropietari[oa]\b|\bdue[ñn][oa]\b",
    "sin costo": r"\bsin\s+costo\b|\bgratuit\w*|\bgratis\b|\bcedid[oa]\b",
}
_SIN_DATO = {           # atributos que no están en los datos: si el texto los afirma, los inventó
    "persona sola": r"\bpersona\s+sola\b|\bsolter[oa]\b|\bcasad[oa]\b|\bdivorciad[oa]\b|\bviud[oa]\b",
    "hijos o familia": r"\bhij[oa]s?\b|\bfamilia\b|\bdependientes\b",
    "empleo o ingresos": r"\bdesemple\w+|\bempleo\b|\bemplead[oa]\b|\btrabaj\w+|\bingresos?\b|\bsalario\b|\bsueldo\b",
}


def _afirma(patron, texto):
    """True si el patrón aparece en el texto sin una negación («no», «sin», «ni») en las tres palabras anteriores."""
    for m in re.finditer(patron, texto):
        antes = texto[:m.start()].split()[-3:]
        if not any(p in ("no", "sin", "ni", "tampoco") for p in antes):
            return True
    return False


def verificar_datos(texto, datos):
    """Devuelve una lista de problemas: afirmaciones del texto que contradicen los datos o que no tienen dato."""
    t = texto.lower()
    problemas = []
    cuenta = datos.get("cuenta corriente")
    if cuenta in _CUENTA:
        if cuenta == "saldo negativo" and re.search(_NIEGA_SALDO_NEG, t):
            problemas.append("dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»")
        for categoria, patron in _CUENTA.items():
            if categoria != cuenta and _afirma(patron, re.sub(_NIEGA_SALDO_NEG, " ", t)):
                problemas.append(f"habla de «{categoria}» en la cuenta corriente, pero el dato es «{cuenta}»")
    vivienda = datos.get("vivienda")
    if vivienda in _VIVIENDA:
        sin_costo = re.sub(_VIVIENDA["sin costo"], " ", t)                # «sin costo» no es una afirmación de alquiler
        for categoria, patron in _VIVIENDA.items():
            if categoria != vivienda and _afirma(patron, t if categoria == "sin costo" else sin_costo):
                problemas.append(f"dice que la vivienda es «{categoria}», pero el dato es «{vivienda}»")
    for atributo, patron in _SIN_DATO.items():
        if _afirma(patron, t):
            problemas.append(f"afirmación sin dato que la respalde: {atributo}")
    return problemas


def explicacion_segura(datos, prob):
    """Texto de respaldo, armado solo con datos y la probabilidad. No usa el modelo de lenguaje."""
    nivel = "bajo" if prob < 0.30 else ("medio" if prob <= 0.60 else "alto")   # mismos umbrales que verificar_tono
    detalle = ", ".join(f"{k}: {v}" for k, v in datos.items())                 # los datos de la solicitud
    return f"El modelo estima una probabilidad de {prob:.0%} de que el crédito sea malo (riesgo {nivel}). Datos: {detalle}."


def verificar_base(texto, datos, prob):
    """El verificador de clase (solo números y tono en franjas extremas). Se conserva para medir el «antes»."""
    return verificar_numeros(texto, datos, prob) + verificar_tono(texto, prob)


def verificar_explicacion(texto, datos, prob):
    """Reúne todas las verificaciones. Lista vacía = el texto se puede mostrar."""
    return verificar_base(texto, datos, prob) + verificar_datos(texto, datos)
