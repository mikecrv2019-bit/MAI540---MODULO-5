---
description: Audita el predictor por tipo de vivienda y entrega una ficha de hallazgo con su nivel de fiabilidad
allowed-tools: Bash(python tareas.py vivienda:*)
---
## Contexto
Resultado del predictor por tipo de vivienda, sobre los casos de prueba (`malos_reales` es la proporción de créditos malos que hay en el grupo y `malos_detectados` la proporción de esos créditos malos que el modelo señaló):
!`python tareas.py vivienda`

## Tu tarea
Entrega una ficha con exactamente estos cuatro encabezados, una o dos líneas bajo cada uno:

**Hallazgo.** El grupo donde el modelo se comporta peor y en qué métrica. Compara `exactitud` con `malos_detectados`: si la exactitud es parecida entre grupos pero los malos detectados no, dilo, porque la exactitud estaría ocultando el problema.
**Evidencia.** Las cifras de la tabla que lo respaldan, con el número de casos de cada grupo.
**Fiabilidad.** ALTA, MEDIA o BAJA. Es BAJA si el grupo tiene menos de 30 casos (columna `aviso`); explica en una frase por qué un promedio con pocos casos no es de fiar.
**Siguiente comprobación.** Una sola acción concreta antes de decidir algo con este hallazgo.

No inventes cifras que no estén en la tabla. No modifiques ningún archivo.
