"""Ejecuta la aplicación híbrida: predice, explica con el modelo de lenguaje y verifica la explicación."""
from datos import datos_legibles
from explicador import cargar_modelo_lenguaje, explicar, recortar_a_oracion
from predictor import entrenar_predictor, probabilidad_malo
from verificador import explicacion_segura, verificar_explicacion

print("Entrenando el modelo predictivo...")
predictor, X_pru, y_pru = entrenar_predictor()                    # modelo + casos que nunca vio
print("Cargando el modelo de lenguaje (la primera vez se descarga)...")
tokenizador, modelo = cargar_modelo_lenguaje()

rechazadas = 0
for i in range(6):                                                # seis solicitudes de prueba
    datos = datos_legibles(X_pru.iloc[i])                         # datos en español
    prob = probabilidad_malo(predictor, X_pru, i)                 # lo que predice el modelo
    texto = recortar_a_oracion(explicar(tokenizador, modelo, datos, prob))   # lo que redacta (solo frases completas)
    problemas = verificar_explicacion(texto, datos, prob)         # lo que verificamos
    final = explicacion_segura(datos, prob) if problemas else texto
    rechazadas += bool(problemas)
    print(f"\n--- Solicitud {i + 1} | probabilidad de crédito malo: {prob:.0%} | real: {'malo' if y_pru.iloc[i] else 'bueno'}")
    print("Modelo de lenguaje:", texto)
    print("Verificación:", "OK" if not problemas else "; ".join(problemas))
    print("Se muestra:", final)
print(f"\nExplicaciones rechazadas por la verificación: {rechazadas} de 6")
