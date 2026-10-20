"""Ejecuta la aplicación híbrida: predice, explica con el modelo de lenguaje y verifica la explicación.

Uso:  python main.py [N] [--regenerar]
  N            número de solicitudes de prueba a recorrer (por defecto 20; la tarea pide 10 o más).
  --regenerar  vuelve a pedir los textos al modelo de lenguaje en lugar de reutilizar los guardados.

Los textos se guardan en evidencia/textos_generados.json. La generación es determinista (do_sample=False), así que
reutilizarlos da el mismo resultado y permite medir verificadores distintos sobre exactamente los mismos textos.
"""
import json
import os
import sys

from datos import datos_legibles
from explicador import cargar_modelo_lenguaje, explicar, recortar_a_oracion
from predictor import entrenar_predictor, probabilidad_malo
from verificador import explicacion_segura, verificar_explicacion

SALIDA = os.path.join("evidencia", "textos_generados.json")
argumentos = [a for a in sys.argv[1:] if not a.startswith("--")]
N = int(argumentos[0]) if argumentos else 20                      # solicitudes a recorrer
REGENERAR = "--regenerar" in sys.argv

guardados = {}
if os.path.exists(SALIDA) and not REGENERAR:
    with open(SALIDA, encoding="utf-8") as f:
        guardados = {r["solicitud"]: r for r in json.load(f)}     # textos ya generados, por número de solicitud

print("Entrenando el modelo predictivo...")
predictor, X_pru, y_pru = entrenar_predictor()                    # modelo + casos que nunca vio
tokenizador = modelo = None                                       # el modelo de lenguaje se carga solo si hace falta

def guardar(registros):
    """Guarda los textos fusionados con los que ya había, para que correr con un N menor no borre los demás."""
    todos = {**guardados, **{r["solicitud"]: r for r in registros}}
    os.makedirs("evidencia", exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8") as f:
        json.dump([todos[k] for k in sorted(todos)], f, ensure_ascii=False, indent=2)


rechazadas = 0
registros = []
for i in range(N):                                                # solicitudes de prueba
    datos = datos_legibles(X_pru.iloc[i])                         # datos en español
    prob = probabilidad_malo(predictor, X_pru, i)                 # lo que predice el modelo
    previo = guardados.get(i + 1)
    if previo and previo["datos"] == datos:
        texto = previo["texto"]                                   # reutiliza el texto ya generado
    else:
        if modelo is None:
            print("Cargando el modelo de lenguaje (la primera vez se descarga)...")
            tokenizador, modelo = cargar_modelo_lenguaje()
        texto = recortar_a_oracion(explicar(tokenizador, modelo, datos, prob))   # lo que redacta (solo frases completas)
    problemas = verificar_explicacion(texto, datos, prob)         # lo que verificamos
    final = explicacion_segura(datos, prob) if problemas else texto
    rechazadas += bool(problemas)
    real = "malo" if y_pru.iloc[i] else "bueno"
    registros.append({"solicitud": i + 1, "datos": datos, "prob": prob, "real": real, "texto": texto})
    print(f"\n--- Solicitud {i + 1} | probabilidad de crédito malo: {prob:.0%} | real: {real}")
    print("Datos:", "; ".join(f"{k}: {v}" for k, v in datos.items()))
    print("Modelo de lenguaje:", texto)
    print("Verificación:", "OK" if not problemas else "; ".join(problemas))
    print("Se muestra:", final)
    if modelo is not None and (i + 1) % 10 == 0:                  # guarda el avance por si se interrumpe una corrida larga
        guardar(registros)
print(f"\nExplicaciones rechazadas por la verificación: {rechazadas} de {N}")

guardar(registros)
print(f"Textos guardados en {SALIDA}")
