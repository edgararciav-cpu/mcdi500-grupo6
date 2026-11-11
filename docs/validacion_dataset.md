# Validación del dataset — MCDI500

**Archivo:** `incidencias_oct2026_anon.csv` · 21542 filas × 49 columnas

## Perfil de variables

| variable | dtype | rol | unicos | pct_nulos |
| --- | --- | --- | --- | --- |
| </div>ï»¿TT | str | alta cardinalidad | 19915 | 0.0 |
| Fecha de Inicio de incidencia | str | fecha | 14997 | 0.0 |
| Fecha de Inicio ticket | str | fecha | 4598 | 0.0 |
| Comuna | str | alta cardinalidad | 335 | 1.6 |
| Estado | str | nominal | 4 | 0.0 |
| Tipo Incidencia NOC | str | nominal | 14 | 0.0 |
| Incidencia NOC | str | alta cardinalidad | 30 | 0.0 |
| Criticidad | str | nominal | 7 | 0.0 |
| Detalle | str | alta cardinalidad | 2709 | 0.0 |
| Impacto | str | nominal | 4 | 0.0 |
| Tiempo de Respuesta | int64 | discreta | 5 | 0.0 |
| Titulo | str | alta cardinalidad | 3068 | 78.5 |
| Q Network Element | int64 | discreta | 35 | 0.0 |
| Network Element | str | alta cardinalidad | 3452 | 0.0 |
| Proveedor | str | alta cardinalidad | 69 | 86.0 |
| Ticket de proveedor | str | alta cardinalidad | 275 | 92.3 |
| Incident Manager | str | nominal | 8 | 78.5 |
| Creador de TT | str | alta cardinalidad | 36 | 0.0 |
| Fecha Cierre de incidencia | str | fecha | 11014 | 24.7 |
| Fecha de Cierre de ticket | str | fecha | 3910 | 27.2 |
| Tiempo de duraciÃ³n de la incidencia | str | alta cardinalidad | 9822 | 24.7 |
| Tiempo de duraciÃ³n del ticket | str | alta cardinalidad | 4173 | 27.2 |
| CÃ³digo de Servicio | str | alta cardinalidad | 1090 | 89.5 |
| Tramo Afectado | str | nominal | 5 | 98.4 |
| Comunas | str | alta cardinalidad | 519 | 0.0 |
| Regiones | str | alta cardinalidad | 29 | 0.2 |
| Causa Raiz NOC | str | alta cardinalidad | 54 | 78.5 |
| Tipo Incidencia GMI | str | nominal | 7 | 93.5 |
| Incidenca GMI | str | alta cardinalidad | 18 | 93.5 |
| Causa Raiz GMI | str | alta cardinalidad | 44 | 93.5 |
| Horario Posible DegradaciÃ³n | str | nominal | 1 | 100.0 |
| ETR | str | fecha | 18 | 99.9 |
| Gestionable | str | binaria | 2 | 0.0 |
| Gestor Uptime | str | binaria | 2 | 0.0 |
| Proveedor TX 1 | str | nominal | 10 | 97.5 |
| CÃ³digo servicio TX 1 | str | alta cardinalidad | 147 | 97.5 |
| DescripciÃ³n TX 1 | str | binaria | 2 | 100.0 |
| Proveedor TX 2 | str | binaria | 2 | 99.9 |
| CÃ³digo servicio TX 2 | str | nominal | 7 | 99.9 |
| DescripciÃ³n TX 2 | str | nominal | 1 | 99.9 |
| Proveedor TX 3 | str | binaria | 2 | 100.0 |
| CÃ³digo servicio TX 3 | str | binaria | 2 | 100.0 |
| DescripciÃ³n TX 3 | str | nominal | 1 | 100.0 |
| Proveedor TX 4 | str | binaria | 2 | 100.0 |
| CÃ³digo servicio TX 4 | str | binaria | 2 | 100.0 |
| DescripciÃ³n TX 4 | str | nominal | 1 | 100.0 |
| Proveedor TX 5 | str | nominal | 1 | 100.0 |
| CÃ³digo servicio TX 5 | str | nominal | 1 | 100.0 |
| DescripciÃ³n TX 5 | str | nominal | 1 | 100.0 |

## Requisitos del curso

| estado | requisito | detalle |
| --- | --- | --- |
| OK | Al menos 2000 filas | 21542 filas |
| OK | Al menos 12 columnas | 49 columnas |
| OK | Combina al menos 3 roles analíticos | alta cardinalidad, nominal, binaria, fecha, discreta |
| OK | Al menos una variable numérica | 2 numéricas (continuas o discretas) |
| OK | Al menos una variable categórica | 24 categóricas (nominales, binarias u ordinales) |
| OK | Presencia de valores faltantes | máximo 100.0% en una variable |
| AVISO | Ninguna variable sobre 60% de faltantes | máximo 100.0% |
| OK | Incluye alguna variable de fecha | 5 detectadas |
| OK | Incluye texto o categórica de alta cardinalidad | 18 detectadas |
| OK | Archivo bajo 100 MB | 5.6 MB |
| OK | Sin filas duplicadas exactas | ninguna |

## Resultado

El conjunto **cumple** los requisitos mínimos.