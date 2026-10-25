"""Figuras del informe y la presentacion (Tarea 8.2), dibujadas con los JSON de evidencia/ (no recalcula nada).

    python src/figuras_informe.py

Genera evidencia/fig_errores_confianza.png y evidencia/fig_degradacion.png.
"""
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from datos import RAIZ  # noqa: E402

EVIDENCIA = RAIZ / "evidencia"
TINTA, TINTA_SUAVE, REJILLA = "#1f2933", "#52606d", "#e4e7eb"
AZUL, NARANJA = "#2a6fdb", "#d9730d"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.edgecolor": REJILLA, "axes.labelcolor": TINTA_SUAVE,
                     "xtick.color": TINTA_SUAVE, "ytick.color": TINTA_SUAVE, "axes.spines.top": False, "axes.spines.right": False})


def _cargar(nombre):
    return json.loads((EVIDENCIA / nombre).read_text(encoding="utf-8"))


def fig_errores_por_confianza():
    grupos = _cargar("errores_detalle.json")["por_confianza"]
    etiquetas = [g["grupo"].replace("confianza ", "").replace(" a ", " – ") for g in grupos]
    tasas = [100 * g["tasa_error"] for g in grupos]
    bajo = [100 * (g["tasa_error"] - g["ic95"][0]) for g in grupos]
    alto = [100 * (g["ic95"][1] - g["tasa_error"]) for g in grupos]
    fig, ax = plt.subplots(figsize=(6.4, 3.4), dpi=200)
    colores = [NARANJA if g["errores"] else AZUL for g in grupos]
    ax.bar(etiquetas, tasas, color=colores, width=0.55)
    ax.errorbar(etiquetas, tasas, yerr=[bajo, alto], fmt="none", ecolor=TINTA_SUAVE, elinewidth=1, capsize=4)
    for i, g in enumerate(grupos):
        ax.text(i, 100 * g["ic95"][1] + 2, f"{g['errores']} de {g['n']}", ha="center", color=TINTA, fontsize=9)
    ax.set_ylim(0, 65)
    ax.set_ylabel("Tasa de error (%) e IC 95 % de Wilson")
    ax.set_xlabel("Confianza de la predicción (probabilidad de la clase elegida)")
    ax.yaxis.grid(True, color=REJILLA, linewidth=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(EVIDENCIA / "fig_errores_confianza.png")
    plt.close(fig)


def fig_degradacion():
    esc = _cargar("degradacion.json")["escenarios"]
    nombres = list(esc)
    y = range(len(nombres))[::-1]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.0, 3.6), dpi=200, sharey=True, gridspec_kw={"width_ratios": [1, 1.15]})
    exact = [100 * esc[n]["exactitud_media"] for n in nombres]
    a1.barh(list(y), exact, color=AZUL, height=0.55)
    for yi, v in zip(y, exact):
        a1.text(v + 0.3, yi, f"{v:.1f}", va="center", color=TINTA, fontsize=9)
    a1.set_xlim(80, 100)
    a1.set_xlabel("Exactitud (%), eje desde 80")
    a1.set_yticks(list(y), nombres)
    a1.text(0, 1.2, "Cuánto acierta", transform=a1.transAxes, fontsize=10, color=TINTA)
    ks = [100 * esc[n]["alerta_distribucion"] for n in nombres]
    rango = [100 * esc[n]["alerta_rango"] for n in nombres]
    h = 0.27
    a2.barh([yi + h / 2 + 0.02 for yi in y], ks, color=AZUL, height=h, label="Alerta por distribución (KS)")
    a2.barh([yi - h / 2 - 0.02 for yi in y], rango, color=NARANJA, height=h, label="Alerta por rango")
    a2.set_xlim(0, 100)
    a2.text(0, 1.2, "Cuánto avisa", transform=a2.transAxes, fontsize=10, color=TINTA)
    a2.set_xlabel("% de repartos en que salta la alerta")
    a2.legend(frameon=False, loc="lower right", bbox_to_anchor=(1.0, 1.0), ncol=2, fontsize=8, handlelength=1)
    for ax in (a1, a2):
        ax.xaxis.grid(True, color=REJILLA, linewidth=0.8)
        ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(EVIDENCIA / "fig_degradacion.png")
    plt.close(fig)


if __name__ == "__main__":
    EVIDENCIA.mkdir(exist_ok=True)
    fig_errores_por_confianza()
    fig_degradacion()
    print("Figuras guardadas en", EVIDENCIA)
