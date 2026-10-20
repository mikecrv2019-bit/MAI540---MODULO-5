"""Tarea 7.2 · Punto 1: la red neuronal frente al Random Forest, sobre las mismas 200 solicitudes de prueba.

Uso:  python comparar_modelos.py
Misma partición que entrenar_predictor: test_size=0.20, stratify=y, random_state=42.
"""
from sklearn.model_selection import train_test_split

from datos import cargar_datos
from predictor import entrenar_predictor
from red_neuronal import crear_red, describir_red


def comparar():
    """Entrena la red con el 80% y devuelve un diccionario con capas, pesos y exactitudes (prueba y entrenamiento)."""
    X, y, cols_cat, cols_num = cargar_datos()
    X_ent, X_pru, y_ent, y_pru = train_test_split(X, y, test_size=0.20, stratify=y, random_state=42)
    red = crear_red(cols_cat, cols_num).fit(X_ent, y_ent)
    capas, pesos = describir_red(red)
    rf, X_pru_rf, y_pru_rf = entrenar_predictor()
    assert X_pru.index.equals(X_pru_rf.index), "las dos particiones deben ser las mismas 200 solicitudes"
    base = float((y_pru == 0).mean())                                    # exactitud de decir siempre «bueno»
    def exactitud(modelo, X_, y_):
        return float((modelo.predict(X_) == y_.values).mean())
    def recall_malo(modelo):
        pred = modelo.predict(X_pru)
        return float(((pred == 1) & (y_pru.values == 1)).sum() / (y_pru.values == 1).sum())
    return {
        "n_prueba": len(X_pru), "malos_en_prueba": int(y_pru.sum()), "base_siempre_bueno": base,
        "red_capas": capas, "red_pesos": pesos,
        "red_prueba": exactitud(red, X_pru, y_pru), "red_entrenamiento": exactitud(red, X_ent, y_ent),
        "rf_prueba": exactitud(rf, X_pru, y_pru), "rf_entrenamiento": exactitud(rf, X_ent, y_ent),
        "red_recall_malo": recall_malo(red), "rf_recall_malo": recall_malo(rf),
        "rf_arboles": len(rf.named_steps["modelo"].estimators_),
        "rf_nodos": int(sum(a.tree_.node_count for a in rf.named_steps["modelo"].estimators_)),
    }


if __name__ == "__main__":
    r = comparar()
    print(f"Solicitudes de prueba: {r['n_prueba']} ({r['malos_en_prueba']} malas) | exactitud de decir siempre «bueno»: {r['base_siempre_bueno']:.3f}")
    print(f"Red neuronal   capas {r['red_capas']} | pesos aprendidos: {r['red_pesos']:,}")
    print(f"               exactitud ENTRENAMIENTO {r['red_entrenamiento']:.3f} | PRUEBA {r['red_prueba']:.3f} | malos detectados {r['red_recall_malo']:.3f}")
    print(f"Random Forest  {r['rf_arboles']} árboles, {r['rf_nodos']:,} nodos en total")
    print(f"               exactitud ENTRENAMIENTO {r['rf_entrenamiento']:.3f} | PRUEBA {r['rf_prueba']:.3f} | malos detectados {r['rf_recall_malo']:.3f}")
