# Auditoria por subgrupo: HistGradientBoosting

Predicciones fuera de pliegue (CV estratificada de 5, semilla 42). Variables sensibles solo para agrupar.

Recall global de bad = 0.5100. Umbral 0.1; minimo 20 positivos.

| Subgrupo | Valor | n | bad | Recall bad | Dif. vs global | Exactitud | Estado |
|---|---|---|---|---|---|---|---|
| age_grupo | 25-34 | 399 | 131 | 0.4733 | -0.0367 | 0.7243 | dentro |
| age_grupo | 35-44 | 251 | 58 | 0.4828 | -0.0272 | 0.8247 | dentro |
| age_grupo | <25 | 149 | 61 | 0.5738 | +0.0638 | 0.7181 | dentro |
| age_grupo | >=45 | 201 | 50 | 0.5600 | +0.0500 | 0.8109 | dentro |
| personal_status | female div/dep/mar | 310 | 109 | 0.5138 | +0.0038 | 0.7581 | dentro |
| personal_status | male div/sep | 50 | 20 | 0.3000 | -0.2100 | 0.5800 | supera umbral |
| personal_status | male mar/wid | 92 | 25 | 0.4800 | -0.0300 | 0.7174 | dentro |
| personal_status | male single | 548 | 146 | 0.5411 | +0.0311 | 0.7956 | dentro |
| housing | for free | 108 | 44 | 0.6136 | +0.1036 | 0.7407 | supera umbral |
| housing | own | 713 | 186 | 0.4624 | -0.0476 | 0.7756 | dentro |
| housing | rent | 179 | 70 | 0.5714 | +0.0614 | 0.7430 | dentro |
