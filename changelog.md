# Registro de cambios

Cada entrada indica la fecha, qué cambió, el commit que lo respalda y la justificación técnica. Los commits
se pueden verificar con `git show <commit>`. Las fases siguen el proyecto ABP: F1 definición, F2 datos,
F3 núcleo algorítmico y F4 comunicación. El detalle paso a paso está en `docs/bitacora_proceso.md`.

## Observaciones formativas y acciones de mejora

Observaciones del docente en la Sumativa 1 (12-11-2026) y lo que se hizo con cada una.

| Observación | Acción de mejora | Commit | Impacto |
|---|---|---|---|
| Datos internos con sitios reales en un repositorio público | Repositorio privado; sitios, códigos de servicio y tramos reemplazados por códigos; texto libre omitido; historial reescrito | `1e004ac`, `0c97d30` | Documentación: ningún identificador real queda en el repositorio ni en su historial |
| Objetivos de proceso, no analíticos | Objetivo general y cuatro específicos que responden la pregunta; la preparación de datos pasa a metodología | `213015b` | Documentación: cada figura de F4 responde un objetivo |
| `requirements.txt` con 105 paquetes, uno solo de Windows | Solo las 6 librerías del proyecto, con versión fija, e instalación probada en Linux, macOS y Windows | `0676823`, `52efc82` | Reproducibilidad: el entorno se instala igual en cualquier sistema |
| Los 31 commits de F1 y F2 son del mismo día | Ramas por componente con pull request y commits repartidos entre el 15 y el 19 de noviembre | PR #1 a #4 y rama `f4-visualizacion` | Control de versiones: el historial muestra la evolución por etapas |
| Limitación de las duraciones imputadas sin declarar | La tabla limpia no inventa cierres y la limitación se declara en F2, F3 y F4 | `9e7df9d` | Documentación: el análisis no usa duraciones que no ocurrieron |
| Las piezas que aprenden de los datos son celdas sueltas | Clase base `Transformador` y cinco clases que aprenden con `ajustar` y aplican con `transformar` | `fcad3ed` | Modularidad: cambiar la imputación toca un solo archivo |
| Verificar que las clases dan lo mismo que F2 | Prueba de equivalencia byte a byte (SHA-256) contra los archivos de F2 | `2f45c60` | Validación: las mejoras no cambiaron el resultado |
| Pruebas dispersas | Pruebas en `tests/` que corren con un solo comando (59 en total) | `2f45c60`, `919d5c0`, `ffc94c6` | Validación: casos normales, límite y de excepción repetibles |

Observaciones del docente en la Sumativa 2 (21-11-2026) y lo que se hizo con cada una.

| Observación | Acción de mejora | Commit | Impacto |
|---|---|---|---|
| `Transformador` no es una clase abstracta real | Hereda de `ABC`, con `aprender` y `aplicar` abstractos; dos pruebas nuevas | `525f631` | POO: el contrato se exige al crear el objeto |
| Objetivo 1: informar aparte las incidencias abiertas | `resumen_abiertas` y tabla en F4: 3 abiertas en 3 sitios, ninguno en la lista | `ffc94c6`, `734f871` | Resultados: no se subestima el tiempo de ningún sitio |
| Objetivo 3: falta un denominador | Se declara que las cifras son absolutas y se usa «concentra» en vez de «origina» | `734f871` | Discusión: no se atribuye causa ni confiabilidad sin datos |
| Objetivo 4: criterio con pesos y sensibilidad | `puntaje_prioridad`, `sensibilidad_prioridad` y `sitios_estables`; tabla en `docs/` | `ffc94c6`, `2481bc8` | Resultados: tres sitios se escalan con cualquier criterio |
| Mapa de calor por día | Figura 4, con `fallas_por_dia` y control de que cada fila suma las fallas del sitio | `734f871`, `2481bc8` | Visualización: seis sitios caen los mismos días |
| Fuente y unidades en cada figura | Fuente «NOC, octubre de 2026, datos anonimizados» y unidades en los ejes | `734f871` | Comunicación: cada figura se lee sola |
| Guardar el registro de la última ejecución de las pruebas | `docs/registro_pruebas.txt`, escrito por el notebook F4 | `2481bc8` | Validación: la evidencia queda en el repositorio |
| Commits en bloque | Un commit por cada parte terminada, en la rama `f4-mejoras` | `525f631` a `2481bc8` | Control de versiones: el historial muestra la evolución |

## [F4] 2026-11-24 · Mejoras tras la retroalimentación de la Sumativa 2

### Cambiado
- `Transformador` es una clase abstracta con `ABC` (`525f631`). F3 se ejecutó de nuevo sin cambios en `data/processed` (`1ebb20e`).
- La figura 2 dice «concentra» y declara que las cifras son absolutas, porque no hay inventario de sitios por tipo de enlace (`734f871`).

### Agregado
- Criterio de prioridad con pesos y prueba de sensibilidad (`ffc94c6`). Con pesos iguales coinciden 7 de los 10 sitios de la lista oficial; SIT_2201, SIT_1174 y SIT_1764 están en todas las versiones.
- Incidencias abiertas aparte y figura 4, mapa de calor de fallas por día (`734f871`, `2481bc8`).
- Registro de las 59 pruebas en `docs/registro_pruebas.txt` (`2481bc8`).

### Corregido
- El registro de pruebas se guardaba con los códigos de color de la consola (`92f3c80`).

## [F4] 2026-11-19 · Visualización y comunicación

### Agregado
- Módulo `src/comunicacion.py` y 17 pruebas en `tests/test_comunicacion.py` (`919d5c0`). Lee las tablas de la Fase 3, verifica el contrato de la tabla por sitio y calcula las cifras que se grafican. Son funciones y no clases porque no guardan estado entre llamadas, que es el criterio usado en F3.
- Notebook `F4/F4_Visualizacion_Comunicacion.ipynb` (`da3c729`) con tres figuras, una por objetivo, cuyo título dice el hallazgo. Se grafica con la tabla interpretable y no con la de modelo, que está escalada y en columnas 0/1.
- Ejecución completa de F4 (`33651e5`): figuras en `F4/figuras/` y hallazgos, lista de escalamiento, mediciones y metadatos en `docs/`.

### Verificado
- La tabla de recurrencia se recalcula desde `incidencias_limpio.csv` y es idéntica a la de la Fase 2 (`assert_frame_equal`, `da3c729`). Las figuras descansan sobre el mismo resultado documentado antes.
- La curva de concentración se calcula con dos versiones que dan el mismo resultado. La ingenua es O(n²) y la vectorizada O(n log n): con 5.000 sitios, la vectorizada es unas 600 veces más rápida y queda como la definitiva (`33651e5`, `docs/mediciones_eficiencia_f4.csv`).

## [F3] 2026-11-15 a 2026-11-18 · Núcleo algorítmico, eficiencia y POO

### Cambiado
- `requirements.txt` solo con las librerías del proyecto (`0676823`) y prueba de instalación en tres sistemas con GitHub Actions (`52efc82`). Responde a la observación de reproducibilidad.
- Anonimización: sitios con código y texto libre omitido (`1e004ac`). Desde el 17-11 también se codifican los códigos de servicio y los tramos (`0c97d30`). Responde a la corrección obligatoria sobre los datos.
- Objetivos analíticos y metodología en F1 (`213015b`). Responde a la observación de problemática.

### Agregado
- Funciones de F2 que no aprenden de los datos, trasladadas a `src/limpieza.py` (`b5ce606`).
- Clase base `Transformador` y clases hijas que aprenden de los datos, con herencia, polimorfismo y encapsulamiento (`fcad3ed`).
- `Pipeline` que ejecuta la Fase 2 en una llamada, con la bitácora como observador (patrón Observer) y el `Escalador` con patrón Strategy (`d7ef4a8`).
- Medición con `timeit` y `tracemalloc`, y fusión de intervalos iterativa (`18d2d85`).
- 30 pruebas de casos normales, límite y excepción, más la equivalencia con F2 (`2f45c60`).
- `.mailmap` para que Git muestre una sola identidad del autor (`dd5a032`).

### Optimizado
- Vacíos vectorizados (unas 2 veces más rápido) y fusión iterativa por defecto, porque la recursiva crece en memoria y falla con RecursionError sobre unos 1.000 intervalos de un mismo sitio (`daed972`).

### Corregido
- `UnificadorVariantes` borraba las categorías que no vio al ajustar. Apareció al separar entrenamiento y prueba (`f9539aa`).

## [F1 y F2] 2026-11-11 · Definición, entorno y pipeline de datos

### Agregado
- Estructura del repositorio, entorno reproducible y módulo `utilidades` con excepción propia (`c7469f7`, `ed3bcfd`, `70a2144`).
- Notebook F1: problema, entorno, ficha, diccionario y validación del conjunto (`7ab07a0`).
- Notebook F2: limpieza, transformación, escalamiento y validación (`bb16016`).
- Recurrencia por sitio con las reglas del NOC (`954d6f4`) y corte del uptime al 31-10 (`69aca6d`).

### Corregido
- Textos de F1, F2 y del mapa conceptual según la auditoría previa a la entrega (`beb5b5e`).
