"""Comprueba un bloque del proyecto sin escribir comandos largos.

Uso:  python verificar.py <número de TODO>      Ejemplo:  python verificar.py 2
"""
import sys

ARCHIVOS = {1: "predictor.py", 2: "predictor.py", 3: "red_neuronal.py", 4: "red_neuronal.py", 5: "explicador.py",
            6: "explicador.py", 7: "verificador.py", 8: "verificador.py", 9: "verificador.py"}
DATOS = {"edad": 25, "duración (meses)": 48, "monto": 5951, "cuenta corriente": "saldo negativo", "vivienda": "alquilada"}


def verificar(n):
    if n == 1:
        from predictor import entrenar_predictor
        predictor, X_pru, y_pru = entrenar_predictor()
        print("Casos de prueba:", len(X_pru), "| exactitud en prueba:", round(float((predictor.predict(X_pru) == y_pru.values).mean()), 2))
        print("DEBE VERSE: 200 casos | exactitud cerca de 0.7 a 0.8")
    elif n == 2:
        from predictor import entrenar_predictor, probabilidad_malo
        predictor, X_pru, _ = entrenar_predictor()
        p = probabilidad_malo(predictor, X_pru, 0)
        print("Probabilidad de crédito malo del primer caso:", round(p, 2))
        print("DEBE VERSE: un número entre 0 y 1")
    elif n in (3, 4):
        from datos import cargar_datos
        from red_neuronal import crear_red, describir_red
        X, y, cols_cat, cols_num = cargar_datos()
        red = crear_red(cols_cat, cols_num).fit(X, y)
        if n == 3:
            print("Exactitud de la red sobre los datos de entrenamiento:", round(float((red.predict(X) == y.values).mean()), 2))
            print("DEBE VERSE: un número entre 0.7 y 1.0")
        else:
            capas, pesos = describir_red(red)
            print("Neuronas por capa:", capas, "| pesos aprendidos:", pesos)
            print("DEBE VERSE: capas [61, 16, 8, 1] | 1,137 pesos aprendidos")
    elif n in (5, 6):
        from explicador import cargar_modelo_lenguaje, explicar
        tok, modelo = cargar_modelo_lenguaje()
        if n == 5:
            print("Modelo cargado:", type(modelo).__name__)
            print("DEBE VERSE: Qwen2ForCausalLM")
        else:
            print("Texto generado:", explicar(tok, modelo, DATOS, 0.78))
            print("DEBE VERSE: una explicación en español de una o dos frases (tarda unos segundos)")
    elif n == 7:
        from verificador import verificar_numeros
        print(verificar_numeros("La probabilidad es de 78% y se trata de una persona de más de 60 años.", DATOS, 0.78))
        print("DEBE VERSE: ['número no sustentado: 60']")
    elif n == 8:
        from verificador import verificar_tono
        print(verificar_tono("La probabilidad es de 12%, lo cual es considerado alto.", 0.12))
        print("DEBE VERSE: ['dice que el riesgo es alto, pero la probabilidad es baja']")
    elif n == 9:
        from verificador import explicacion_segura
        print(explicacion_segura(DATOS, 0.78))
        print("DEBE VERSE: una frase con 78% y riesgo alto, y los cinco datos")
    else:
        print("Los TODO 10 y 11 se verifican con:  pytest -v")


if __name__ == "__main__":
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        sys.exit("Uso: python verificar.py <número de TODO>   (por ejemplo: python verificar.py 2)")
    n = int(sys.argv[1])
    try:
        verificar(n)
    except NotImplementedError:
        print(f"Todavía no completas el TODO {n}: abre {ARCHIVOS.get(n, 'el archivo')} y escribe el bloque.")
