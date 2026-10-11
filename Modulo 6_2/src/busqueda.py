"""Busqueda sistematica de hiperparametros del arbol (GridSearchCV) y su medicion honesta.

El mejor puntaje de una busqueda es optimista: la combinacion ganadora se eligio justamente por
ser la mejor en esos mismos pliegues. Por eso se reportan DOS numeros:
  * numero de la busqueda  -> `best_score_` de GridSearchCV sobre todos los datos (optimista);
  * numero honesto         -> validacion cruzada ANIDADA: la busqueda completa se repite dentro de
                              cada pliegue externo, usando solo sus datos de entrenamiento, y se
                              evalua en el pliegue externo que la busqueda nunca vio.
"""
from sklearn.model_selection import GridSearchCV

from validacion import SEMILLA_CV_INTERNA, crear_cv, evaluar

# Espacio de busqueda (parte del resultado). El prefijo 'modelo__' apunta al paso 'modelo' del Pipeline.
PARAM_GRID = {
    "modelo__max_depth": [1, 2, 3, 4, 5, 7, 10, None],   # profundidad maxima (None = sin limite)
    "modelo__min_samples_leaf": [1, 2, 5, 10, 20],       # casos minimos por hoja
}
SCORING = {"exactitud": "accuracy", "recall_bad": "recall"}  # recall de la clase positiva (bad = 1)


def crear_busqueda(pipeline, cv):
    """GridSearchCV: elige por exactitud (refit) y registra tambien el recall de los malos."""
    return GridSearchCV(
        pipeline, PARAM_GRID, scoring=SCORING, refit="exactitud", cv=cv,
        n_jobs=1, return_train_score=False,
    )


def buscar(pipeline, X, y, cv):
    """Busqueda sobre TODOS los datos: da la combinacion ganadora y el numero (optimista) de la busqueda."""
    return crear_busqueda(pipeline, cv).fit(X, y)


def validacion_anidada(pipeline, X, y, cv_externa):
    """Numero honesto: busqueda dentro de cada pliegue externo (cv interna con otra semilla)."""
    busqueda = crear_busqueda(pipeline, crear_cv(SEMILLA_CV_INTERNA))
    return evaluar(busqueda, X, y, cv_externa)


def parametros_limpios(params):
    """{'modelo__max_depth': 5, ...} -> {'max_depth': 5, ...} (None se conserva)."""
    return {k.split("__", 1)[1]: v for k, v in params.items()}
