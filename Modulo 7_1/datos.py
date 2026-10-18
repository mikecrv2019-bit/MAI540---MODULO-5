"""Paso 0 · Datos: lee German Credit y entrega las variables, el objetivo y los tipos de columna."""
import pandas as pd                                         # pandas: trabaja con tablas, como un Excel dentro de Python


def cargar_datos(ruta="datos/credit_g.csv"):
    """Devuelve X (variables), y (1 = crédito malo), cols_cat (texto) y cols_num (números)."""
    df = pd.read_csv(ruta)                                  # lee el archivo y lo guarda como tabla
    y = (df["clase"] == "bad").astype(int)                  # objetivo: 1 si el crédito es malo, 0 si es bueno
    X = df.drop(columns="clase")                            # variables: todas las columnas menos la clase
    cols_cat = X.select_dtypes(exclude="number").columns.tolist()   # columnas con texto (categorías)
    cols_num = X.select_dtypes(include="number").columns.tolist()   # columnas con números
    return X, y, cols_cat, cols_num                         # entrega las cuatro piezas


# Traducciones para que el componente generativo reciba datos legibles y no códigos del dataset.
CUENTA = {"<0": "saldo negativo", "0<=X<200": "saldo entre 0 y 200", ">=200": "saldo de 200 o más", "no checking": "sin cuenta corriente"}
VIVIENDA = {"own": "propia", "rent": "alquilada", "for free": "sin costo"}


def datos_legibles(fila):
    """Convierte una fila de la tabla en un diccionario con los datos clave, en español."""
    return {
        "edad": int(fila["age"]),                           # años del solicitante
        "duración (meses)": int(fila["duration"]),          # plazo del crédito
        "monto": int(fila["credit_amount"]),                # monto solicitado
        "cuenta corriente": CUENTA.get(fila["checking_status"], str(fila["checking_status"])),
        "vivienda": VIVIENDA.get(fila["housing"], str(fila["housing"])),
    }
