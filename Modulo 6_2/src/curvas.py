"""Curva de aprendizaje: exactitud en entrenamiento y en validacion con cantidades crecientes de datos.

Diagnostico: la BRECHA entre ambas curvas indica sobreajuste; si la curva de validacion sigue subiendo
al llegar al maximo de datos, mas datos ayudarian. Usa la misma validacion cruzada que el resto.
"""
import matplotlib
import numpy as np

matplotlib.use("Agg")  # sin ventana: guarda la grafica en archivo
import matplotlib.pyplot as plt
from sklearn.base import clone
from sklearn.model_selection import learning_curve

TAMANOS = np.linspace(0.1, 1.0, 10)   # fracciones del maximo de entrenamiento (800 casos con 5 pliegues)
SEMILLA_MEZCLA = 42                   # mezcla de las filas antes de tomar subconjuntos crecientes


def curva_aprendizaje(pipeline, X, y, cv):
    """Devuelve (tamanos, exactitud_entrenamiento, exactitud_validacion); las dos ultimas son (n_tamanos, n_pliegues)."""
    tamanos, ent, val = learning_curve(
        clone(pipeline), X, y, cv=cv, train_sizes=TAMANOS, scoring="accuracy",
        shuffle=True, random_state=SEMILLA_MEZCLA, n_jobs=1,
    )
    return tamanos, ent, val


def resumen_curva(tamanos, ent, val):
    """Brecha final y pendiente de validacion, ademas de la curva media y su desviacion."""
    me, mv = ent.mean(axis=1), val.mean(axis=1)
    return {
        "tamanos": [int(t) for t in tamanos],
        "entrenamiento_media": [float(v) for v in me],
        "entrenamiento_desv": [float(v) for v in ent.std(axis=1, ddof=1)],
        "validacion_media": [float(v) for v in mv],
        "validacion_desv": [float(v) for v in val.std(axis=1, ddof=1)],
        "brecha_final": float(me[-1] - mv[-1]),
        "validacion_final": float(mv[-1]),
        "entrenamiento_final": float(me[-1]),
        # pendiente de la validacion en la segunda mitad de la curva (recta ajustada a los 5 ultimos puntos),
        # en puntos porcentuales de exactitud por cada 100 casos de entrenamiento adicionales
        "pendiente_validacion_pp_por_100_casos": float(100 * 100 * np.polyfit(tamanos[5:], mv[5:], 1)[0]),
        "tamano_inicio_tramo": int(tamanos[5]),
    }


def graficar(paneles, ruta, base=0.70):
    """paneles: lista de (titulo, resumen_curva). Una fila de paneles con el mismo eje Y."""
    fig, ejes = plt.subplots(1, len(paneles), figsize=(3.2 * len(paneles), 3.0), sharey=True)
    ejes = np.atleast_1d(ejes)
    for ax, (titulo, r) in zip(ejes, paneles):
        t = np.asarray(r["tamanos"])
        for clave, etiqueta, color in (("entrenamiento", "entrenamiento", "tab:blue"),
                                       ("validacion", "validación", "tab:orange")):
            m, d = np.asarray(r[f"{clave}_media"]), np.asarray(r[f"{clave}_desv"])
            ax.plot(t, m, "o-", ms=3, color=color, label=etiqueta)
            ax.fill_between(t, m - d, m + d, color=color, alpha=0.15)
        ax.axhline(base, ls="--", color="gray", lw=1, label="«siempre bueno»")
        ax.set_title(f"{titulo}\nbrecha final {r['brecha_final']:.2f}", fontsize=9)
        ax.set_xlabel("casos de entrenamiento", fontsize=8)
        ax.tick_params(labelsize=8)
        ax.grid(alpha=0.25)
    ejes[0].set_ylabel("exactitud", fontsize=8)
    ejes[0].legend(fontsize=7, loc="center right")
    fig.tight_layout()
    fig.savefig(ruta, dpi=200)
    plt.close(fig)
