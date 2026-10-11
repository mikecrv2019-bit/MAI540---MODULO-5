"""Configuracion del modelo elegido para auditar y probar.

Se fijo DESPUES de ver la comparacion de `busqueda_comparacion.py` (evidencia/busqueda_comparacion.md).
Criterio: el error que mas preocupa es aprobar un credito malo (falso negativo de la clase 'bad'), asi que
entre los modelos con exactitud comparable se prefiere el que detecta mas malos. Justificacion con cifras en
el informe y en la bitacora. Valores validos: arbol_afinado, random_forest, boosting_hgb.
"""
MODELO_ELEGIDO = "boosting_hgb"
