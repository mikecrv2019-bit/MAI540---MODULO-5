# Simulacion de degradacion (generado por `src/simular_degradacion.py`)

Regresion logistica entrenada con 133 lotes y evaluada con 45, en 100 repartos distintos. Los cambios son supuestos, no mediciones reales.

| Escenario | Exactitud (media ± desv.) | Caida | Lotes fuera de rango | Alerta por distribucion (KS) | Alerta por rango | Alguna alerta |
|---|---|---|---|---|---|---|
| sin cambio | 0.983 ± 0.017 | 0.000 | 15% | 1% | 0% | 1% |
| prolina +10 % | 0.978 ± 0.020 | 0.005 | 16% | 1% | 2% | 3% |
| prolina +25 % | 0.970 ± 0.025 | 0.013 | 19% | 21% | 9% | 27% |
| prolina +50 % | 0.943 ± 0.033 | 0.040 | 30% | 100% | 49% | 100% |
| prolina y magnesio +25 % | 0.961 ± 0.032 | 0.022 | 23% | 100% | 18% | 100% |
| ruido 0.5 desv. | 0.950 ± 0.030 | 0.032 | 48% | 6% | 98% | 98% |
| ruido 1.0 desv. | 0.871 ± 0.051 | 0.112 | 81% | 18% | 100% | 100% |

Las columnas de alerta son el % de repartos en que salta cada senal. En la fila 'sin cambio' son falsas alarmas. Distribucion: alguna variable cambia (KS con Bonferroni). Rango: mas del 30 % de los lotes sale del rango de entrenamiento.
