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
    X_ent, X_pru, y_ent, y_pru = train_test_split(X, y, test_size=0.20, stratify=y, random_state=42)   # 80% / 20%
    codificador = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)   # texto → número; categoría nueva → -1
    prep = ColumnTransformer([("cat", codificador, cols_cat)], remainder="passthrough")  # codifica solo el texto
    modelo = RandomForestClassifier(n_estimators=200, random_state=42)                   # 200 árboles que votan
    predictor = Pipeline([("prep", prep), ("modelo", modelo)]).fit(X_ent, y_ent)         # preparar + modelo, entrenado
    return predictor, X_pru, y_pru


def probabilidad_malo(predictor, X, indice):
    """Probabilidad (entre 0 y 1) de que el crédito de la fila `indice` sea malo, según el modelo."""
    fila = X.iloc[[indice]]                                  # una fila como tabla (el doble corchete conserva el formato)
    return float(predictor.predict_proba(fila)[0, 1])        # columna 1 = probabilidad de la clase «malo»
