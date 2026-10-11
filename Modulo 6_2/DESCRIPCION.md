# Descripción de los datos y de las variables (Tarea 6.2)

Archivo: `datos/credit_g.csv` (German Credit; Hofmann, 1994). 1,000 solicitudes de crédito, 20 variables y la
columna objetivo `clase` (`bad` = crédito malo, `good` = crédito bueno). Es el mismo archivo de la Tarea 6.1.

## Objetivo

`clase`: `bad` → `y = 1` (clase de interés: el crédito que se debe detectar); `good` → `y = 0`.
Distribución: 700 `good` y 300 `bad`; la línea base «siempre bueno» acierta 0.70.

## Cuándo se conoce cada variable

Todas las variables describen al solicitante o a la solicitud de crédito y se registran al presentarla (según la
descripción del conjunto de datos); por eso se conocen en el momento de predecir. El código no construye ninguna
columna nueva y ninguna se deriva de `clase`.

| Variable | Qué describe | Papel en el proyecto |
|---|---|---|
| `checking_status` | Estado de la cuenta corriente | Predictora |
| `duration` | Duración del crédito solicitado (meses) | Predictora |
| `credit_history` | Historial crediticio | Predictora |
| `purpose` | Propósito del crédito | Predictora |
| `credit_amount` | Monto solicitado | Predictora |
| `savings_status` | Cuenta de ahorros / bonos | Predictora |
| `employment` | Antigüedad en el empleo actual | Predictora |
| `installment_commitment` | Cuota como porcentaje del ingreso disponible | Predictora |
| `personal_status` | Estado civil y sexo | **Sensible: solo para auditar, prohibida como predictora** |
| `other_parties` | Otros deudores o garantes | Predictora |
| `residence_since` | Tiempo de residencia actual | Predictora |
| `property_magnitude` | Propiedad que posee | Predictora |
| `age` | Edad (años) | **Sensible: solo para auditar, prohibida como predictora** |
| `other_payment_plans` | Otros planes de pago a plazos | Predictora |
| `housing` | Vivienda (propia, alquilada, sin costo) | Predictora; también se audita como subgrupo |
| `existing_credits` | Créditos existentes en este banco | Predictora |
| `job` | Calificación del empleo | Predictora |
| `num_dependents` | Personas a cargo | Predictora |
| `own_telephone` | Teléfono propio | Predictora |
| `foreign_worker` | Trabajador extranjero | Predictora |

## Variables prohibidas como predictoras

`age` y `personal_status` (edad; estado civil y sexo) son atributos protegidos. **Se usan para auditar, no para
decidir**: se excluyen de `X` (`src/datos.py`, `VARIABLES_SENSIBLES`) y solo se emplean para agrupar las
predicciones en la auditoría por subgrupo. `housing` no es un atributo protegido: es predictora y además se audita.
Ninguna predictora es un identificador (el archivo no tiene columna de identificación).
