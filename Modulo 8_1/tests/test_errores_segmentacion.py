"""Pruebas del analisis por categoria y del K-Means exploratorio (criterios (a) y (b) de la propuesta)."""
import pytest

from datos import cargar_datos
from errores import analisis_por_categoria
from segmentacion import SILUETA_PILOTO, segmentar


def test_analisis_por_categoria_con_un_caso_conocido():
    """Recall, precision y confusion calculados a mano: 3 reales de a, 1 error a->b."""
    real = ["class_0"] * 3 + ["class_1"] * 2 + ["class_2"] * 1
    pred = ["class_0", "class_0", "class_1", "class_1", "class_1", "class_2"]
    r = analisis_por_categoria(real, pred)
    assert r["errores"] == 1 and r["total"] == 6
    assert r["por_clase"]["class_0"]["recall"] == pytest.approx(2 / 3)
    assert r["por_clase"]["class_1"]["precision"] == pytest.approx(2 / 3)
    assert r["confusiones"] == [{"real": "class_0", "predicho": "class_1", "n": 1}]


def test_kmeans_cumple_silueta_del_piloto_y_es_estable():
    """Criterio (a): silueta >= 0.2849 (piloto). Criterio (b): ARI medio de remuestreo >= 0.80."""
    X, y = cargar_datos()
    s = segmentar(X, y, n_remuestreos=10)
    assert s["silueta"] >= SILUETA_PILOTO - 5e-5
    assert s["estabilidad_ari"]["media"] >= 0.80
    assert sum(s["tamano_por_grupo"].values()) == 178
