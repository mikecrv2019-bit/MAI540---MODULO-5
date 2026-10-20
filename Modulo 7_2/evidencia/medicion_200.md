### Primeras 200 solicitudes de prueba

| Motivo del rechazo | Antes | Después |
|---|---:|---:|
| número no sustentado | 29 | 29 |
| tono incoherente (<30% o >60%) | 37 | 37 |
| afirmación absoluta | 1 | 1 |
| contradice un dato (cuenta/vivienda) | 0 | 25 |
| afirmación sin dato | 0 | 6 |
| tono incoherente (30% a 60%) | 0 | 65 |
| **Textos rechazados (cada texto cuenta una vez)** | **64 de 200** | **133 de 200** |
| Textos que se muestran tal como los redactó el modelo | 136 | 67 |
| Falsos positivos (rechazó un texto correcto) | 0 | 0 |
| Textos incorrectos que aun así pasaron | 91 | 22 |
| Textos con reservas (afirmación evaluativa sin dato) que pasaron | 8 | 8 |
| Textos correctos que se muestran | 37 | 37 |

Textos rechazados SOLO por las reglas nuevas:
  #3 (56%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (56%) está entre 30% y 60%: el riesgo es medio
  #4 (41%, etiqueta: incorrecto): afirmación sin dato que la respalde: persona sola; dice que el riesgo es alto, pero la probabilidad (41%) está entre 30% y 60%: el riesgo es medio
  #7 (36%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (36%) está entre 30% y 60%: el riesgo es medio
  #8 (43%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (43%) está entre 30% y 60%: el riesgo es medio
  #12 (37%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (37%) está entre 30% y 60%: el riesgo es medio
  #15 (48%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (48%) está entre 30% y 60%: el riesgo es medio
  #17 (43%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (43%) está entre 30% y 60%: el riesgo es medio
  #24 (67%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»
  #25 (42%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (42%) está entre 30% y 60%: el riesgo es medio
  #26 (35%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (35%) está entre 30% y 60%: el riesgo es medio
  #36 (57%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (57%) está entre 30% y 60%: el riesgo es medio
  #37 (50%, etiqueta: incorrecto): afirmación sin dato que la respalde: persona sola; dice que el riesgo es alto, pero la probabilidad (50%) está entre 30% y 60%: el riesgo es medio
  #41 (34%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (34%) está entre 30% y 60%: el riesgo es medio
  #47 (62%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»
  #49 (31%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (31%) está entre 30% y 60%: el riesgo es medio
  #55 (70%, etiqueta: incorrecto): afirmación sin dato que la respalde: persona sola
  #56 (34%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (34%) está entre 30% y 60%: el riesgo es medio
  #59 (49%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (49%) está entre 30% y 60%: el riesgo es medio
  #60 (56%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (56%) está entre 30% y 60%: el riesgo es medio
  #63 (48%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (48%) está entre 30% y 60%: el riesgo es medio
  #71 (39%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (39%) está entre 30% y 60%: el riesgo es medio
  #74 (32%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (32%) está entre 30% y 60%: el riesgo es medio
  #79 (46%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (46%) está entre 30% y 60%: el riesgo es medio
  #81 (64%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»
  #83 (32%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (32%) está entre 30% y 60%: el riesgo es medio
  #86 (46%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (46%) está entre 30% y 60%: el riesgo es medio
  #89 (42%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (42%) está entre 30% y 60%: el riesgo es medio
  #92 (59%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (59%) está entre 30% y 60%: el riesgo es medio
  #93 (34%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (34%) está entre 30% y 60%: el riesgo es medio
  #98 (40%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (40%) está entre 30% y 60%: el riesgo es medio
  #99 (36%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (36%) está entre 30% y 60%: el riesgo es medio
  #100 (38%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (38%) está entre 30% y 60%: el riesgo es medio
  #106 (52%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (52%) está entre 30% y 60%: el riesgo es medio
  #111 (37%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (37%) está entre 30% y 60%: el riesgo es medio
  #113 (52%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (52%) está entre 30% y 60%: el riesgo es medio
  #116 (37%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (37%) está entre 30% y 60%: el riesgo es medio
  #121 (31%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (31%) está entre 30% y 60%: el riesgo es medio
  #123 (39%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (39%) está entre 30% y 60%: el riesgo es medio
  #129 (44%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (44%) está entre 30% y 60%: el riesgo es medio
  #130 (37%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (37%) está entre 30% y 60%: el riesgo es medio
  #131 (34%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (34%) está entre 30% y 60%: el riesgo es medio
  #133 (52%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (52%) está entre 30% y 60%: el riesgo es medio
  #134 (54%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (54%) está entre 30% y 60%: el riesgo es medio
  #135 (32%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (32%) está entre 30% y 60%: el riesgo es medio
  #136 (60%, etiqueta: incorrecto): afirmación sin dato que la respalde: persona sola
  #139 (38%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (38%) está entre 30% y 60%: el riesgo es medio
  #140 (38%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (38%) está entre 30% y 60%: el riesgo es medio
  #141 (44%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (44%) está entre 30% y 60%: el riesgo es medio
  #144 (44%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (44%) está entre 30% y 60%: el riesgo es medio
  #145 (36%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (36%) está entre 30% y 60%: el riesgo es medio
  #146 (41%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (41%) está entre 30% y 60%: el riesgo es medio
  #153 (34%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (34%) está entre 30% y 60%: el riesgo es medio
  #155 (36%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (36%) está entre 30% y 60%: el riesgo es medio
  #157 (49%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (49%) está entre 30% y 60%: el riesgo es medio
  #160 (43%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (43%) está entre 30% y 60%: el riesgo es medio
  #161 (51%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (51%) está entre 30% y 60%: el riesgo es medio
  #165 (38%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (38%) está entre 30% y 60%: el riesgo es medio
  #167 (39%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (39%) está entre 30% y 60%: el riesgo es medio
  #169 (31%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»; dice que el riesgo es alto, pero la probabilidad (31%) está entre 30% y 60%: el riesgo es medio
  #170 (32%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (32%) está entre 30% y 60%: el riesgo es medio
  #171 (32%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (32%) está entre 30% y 60%: el riesgo es medio
  #176 (68%, etiqueta: incorrecto): dice que la cuenta corriente no tiene saldo negativo, pero el dato es «saldo negativo»
  #180 (32%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (32%) está entre 30% y 60%: el riesgo es medio
  #182 (50%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (50%) está entre 30% y 60%: el riesgo es medio
  #184 (52%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (52%) está entre 30% y 60%: el riesgo es medio
  #185 (40%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (40%) está entre 30% y 60%: el riesgo es medio
  #186 (48%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (48%) está entre 30% y 60%: el riesgo es medio
  #189 (20%, etiqueta: incorrecto): afirmación sin dato que la respalde: persona sola
  #199 (32%, etiqueta: incorrecto): dice que el riesgo es alto, pero la probabilidad (32%) está entre 30% y 60%: el riesgo es medio
