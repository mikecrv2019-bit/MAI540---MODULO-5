"""Paso 1 · El modelo predictivo: el Random Forest de la Clase 6, entrenado y listo para dar probabilidades."""
from sklearn.compose import ColumnTransformer           # aplica una transformación solo a ciertas columnas
from sklearn.ensemble import RandomForestClassifier     # el modelo de conjunto de la Clase 6
from sklearn.model_selection import train_test_split    # separa datos de entrenamiento y de prueba
from sklearn.pipeline import Pipeline                   # encadena preparación y modelo
from sklearn.preprocessing import OrdinalEncoder        # convierte texto en números

from datos import cargar_datos


def entrenar_predictor():
    """Entrena con el 80% de los casos y devuelve el predictor y el 20% restante (casos que nunca vio)."""
    X, y, cols_cat, cols_num = cargar_datos()
    # TODO 1 (en clase): separar prueba, armar el Pipeline y entrenar el Random Forest
    raise NotImplementedError("TODO 1: completar en clase")
    return predictor, X_pru, y_pru


def probabilidad_malo(predictor, X, indice):
    """Probabilidad (entre 0 y 1) de que el crédito de la fila `indice` sea malo, según el modelo."""
    # TODO 2 (en clase): predict_proba sobre una sola fila
    raise NotImplementedError("TODO 2: completar en clase")
