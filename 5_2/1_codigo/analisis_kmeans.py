"""
Pasos 3 y 4 de la tarea K-Means sobre 'wine': justificación de k (codo + silueta)
y proyección con el PCA de la Tarea 5.1 coloreada por grupo.

Reutiliza kmeans_utils.ejecutar_kmeans (la misma lógica que expone la tool
segmentar_kmeans) y pca_utils.ejecutar_pca. Escribe en 5_2/3_graficos y 5_2/5_datos_y_logs.

    python analisis_kmeans.py
"""

import json
import sys
from pathlib import Path

# Los scripts viven en 5_2/1_codigo; el código del servidor (kmeans_utils.py,
# pca_utils.py, mcp_server.py, datasets/) está en la raíz del repositorio.
RAIZ = Path(__file__).resolve().parents[2]
TAREA = RAIZ / "5_2"
sys.path.insert(0, str(RAIZ))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

import kmeans_utils
import pca_utils

DATASET = "wine"
GRAFICOS = TAREA / "3_graficos"
DATOS = TAREA / "5_datos_y_logs"
GRAFICOS.mkdir(parents=True, exist_ok=True)
DATOS.mkdir(parents=True, exist_ok=True)

# --- Paso 3: codo + silueta para k = 2..10 -------------------------------
filas = []
for k in range(2, 11):
    r = kmeans_utils.ejecutar_kmeans(DATASET, k)
    filas.append({"k": k, "inercia": r["inercia"], "silueta": r["silueta"]})
tabla = pd.DataFrame(filas)
tabla["caida_inercia"] = (-tabla["inercia"].diff()).round(4)
tabla.to_csv(DATOS / "k_codo_silueta.csv", index=False)
print(tabla.to_string(index=False))

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].plot(tabla.k, tabla.inercia, "o-")
ax[0].set(title="Método del codo (wine)", xlabel="k", ylabel="Inercia")
ax[1].plot(tabla.k, tabla.silueta, "o-", color="tab:green")
ax[1].set(title="Coeficiente de silueta (wine)", xlabel="k", ylabel="Silueta promedio")
for a in ax:
    a.set_xticks(tabla.k)
    a.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(GRAFICOS / "codo_silueta.png", dpi=150)
plt.close()

# --- Paso 4: PCA (2 componentes) coloreado por grupo ---------------------
K = int(tabla.loc[tabla.silueta.idxmax(), "k"])
print(f"\nk con mayor silueta: {K}")
res = kmeans_utils.ejecutar_kmeans(DATASET, K)
etiquetas = np.array(res["etiquetas"])

pca_info = pca_utils.ejecutar_pca(DATASET, 2)  # el PCA de la Tarea 5.1
X, cols = kmeans_utils.cargar_y_escalar(DATASET)
Z = PCA(n_components=2, random_state=42).fit_transform(X)

fig, ax = plt.subplots(figsize=(6.5, 5))
for g in sorted(set(etiquetas)):
    m = etiquetas == g
    ax.scatter(Z[m, 0], Z[m, 1], label=f"Grupo {g} (n={m.sum()})", s=28, alpha=0.8)
v = pca_info["varianza_explicada_por_componente"]
ax.set(
    title=f"wine: K-Means (k={K}) proyectado con PCA",
    xlabel=f"PC1 ({v[0]:.1%} de varianza)",
    ylabel=f"PC2 ({v[1]:.1%} de varianza)",
)
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(GRAFICOS / "pca_kmeans.png", dpi=150)
plt.close()

# --- Perfil de grupos (en unidades originales) para el paso 5 ------------
df = pca_utils.cargar_dataset(DATASET).dropna(subset=cols).reset_index(drop=True)
df["grupo"] = etiquetas
perfil = df.groupby("grupo")[cols].mean().round(2)
perfil.insert(0, "n", df.groupby("grupo").size())
perfil.to_csv(DATOS / "perfil_grupos.csv")
print("\nPerfil (medias originales):\n", perfil.T.to_string())

# z-score de cada grupo vs. media global: qué variables distinguen a cada grupo
z = pd.DataFrame(X, columns=cols)
z["grupo"] = etiquetas
zperfil = z.groupby("grupo")[cols].mean().round(2)
zperfil.to_csv(DATOS / "perfil_grupos_z.csv")
print("\nPerfil (desviaciones estándar vs. media global):\n", zperfil.T.to_string())

# contraste con la etiqueta real (solo informativo, no se usó en K-Means)
print("\nGrupo vs. cultivar real:\n", pd.crosstab(df["grupo"], df["cultivar"]).to_string())

resumen = {
    "k_elegido": K,
    "silueta": res["silueta"],
    "inercia": res["inercia"],
    "tamano_por_grupo": res["tamano_por_grupo"],
    "pca_varianza_por_componente": v,
    "pca_varianza_acumulada_2pc": pca_info["varianza_acumulada"],
    "cargas_PC1_PC2": pca_info["cargas"],
}
(DATOS / "resumen_kmeans.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
print("\nVarianza PCA 2 componentes:", v, "acum:", pca_info["varianza_acumulada"])
