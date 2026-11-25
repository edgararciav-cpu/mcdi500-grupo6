# Fallas recurrentes de transmisión en la red de un operador móvil

Proyecto del curso **MCDI500 · Programación para la Ciencia de Datos** · Magíster en Ciencia de Datos e Inteligencia Artificial, Universidad Andrés Bello.

- **Integrante:** Edgar Arcia Velásquez ([@edgararciav-cpu](https://github.com/edgararciav-cpu)) · Grupo 6
- **Docente:** Dr. Omar Salinas Silva

## Problemática

El NOC registró 21.542 incidencias en octubre de 2026; 588 son fallas de transmisión (enlace de microondas, fibra propia o fibra de proveedor). Varios sitios fallaron más de una vez en el mes, pero no hay una medición que diga cuáles concentran las fallas, cuánto tiempo sin servicio acumulan y con qué tipo de enlace se asocian. Para el uptime cuentan solo las incidencias con pérdida de servicio: criticidad P1, P2, P3 y P3E (P3 extendida, que se trata igual que una P3).

**Pregunta:** ¿Qué sitios de la red concentran incidencias recurrentes de transmisión (microondas, fibra propia FOP y fibra de proveedor), cuánto tiempo fuera de servicio acumulan y con qué tipo de enlace o proveedor se asocian, para priorizar su escalamiento y evaluar cambios de transmisión que mejoren el uptime?

**Objetivo general:** Identificar los sitios con fallas recurrentes de transmisión en octubre de 2026, cuantificar su tiempo fuera de servicio y determinar con qué tipo de enlace y qué proveedor se asocian, para priorizar su escalamiento y evaluar cambios de transmisión que mejoren el uptime.

**Objetivos específicos:**

1. Cuantificar, por sitio, las fallas de transmisión con pérdida de servicio (P1, P2, P3 y P3E) y los minutos que estuvo fuera de servicio en octubre, sin contar dos veces el tiempo de incidencias que se traslapan.
2. Identificar los sitios con fallas recurrentes (dos o más en el mes) y medir qué parte del tiempo fuera de servicio por transmisión concentran.
3. Determinar qué tipo de enlace (microondas, fibra propia FOP, fibra de proveedor o satelital) y qué proveedor de transmisión concentran más fallas y más minutos fuera de servicio.
4. Ordenar los sitios recurrentes en una lista de prioridad para escalar al área de transmisión o al proveedor, con su enlace, su proveedor y su región.

**Metodología:** Los objetivos se responden con un flujo reproducible en cuatro fases: F1 define el problema y mide la calidad de los datos sin corregirlos; F2 limpia, transforma y arma la tabla de recurrencia por sitio; F3 lleva ese pipeline a módulos y clases, verifica que el resultado no cambie y mide su eficiencia; F4 visualiza y comunica los resultados.

## Datos

- **Origen:** Exporte interno del sistema de tickets del NOC de WOM (operador móvil, Chile). Los sitios se reemplazaron por códigos y el texto libre se omitió; el docente está informado.
- **Período:** 2026-10-01 a 2026-10-31 (cierres hasta 2026-11-10).
- **Archivo:** `data/raw/incidencias_oct2026_anon.csv` (21.542 filas × 49 columnas, separador `;`).
- **Anonimización:** scripts/anonimizar_incidencias.py: personas, tickets de proveedor y códigos de servicio TX reemplazados por códigos; los sitios van con un código (SIT_0001, ...) y el texto libre (Titulo y Detalle) se omite. El exporte original no forma parte del repositorio.

## Estructura

```
data/raw/        datos de entrada anonimizados (no se modifican)
data/processed/  resultado de la limpieza y transformación (F2; F3 lo reproduce idéntico)
docs/            diccionario de variables, bitácoras, metadatos, mediciones, hallazgos y vinculación con el mapa
src/             código del proyecto (ver «Arquitectura del código»)
tests/           pruebas de casos normales, límite y excepciones (unittest)
scripts/         preparación previa de los datos (anonimización)
F1/ F2/ F3/ F4/  un notebook por fase (F4/figuras: las figuras del informe)
changelog.md     cambios por fase, con fecha, commit y justificación
```

## Arquitectura del código (Fases 3 y 4)

| Módulo | Responsabilidad | Usa a |
|---|---|---|
| `src/utilidades.py` | Funciones base de las Fases 1 y 2: texto, duraciones, sitios y fusión de intervalos (recursiva e iterativa) | — |
| `src/carga.py` | Lee `data/raw` y verifica que sea el archivo que registró la Fase 1 | utilidades |
| `src/limpieza.py` | Operaciones que **no** aprenden de los datos (funciones) | utilidades |
| `src/transformadores.py` | Pasos que **sí** aprenden de los datos: clase base `Transformador` y cinco clases hijas, más el adaptador `PasoFijo` | utilidades |
| `src/pipeline.py` | `Pipeline` que encadena los 15 pasos, `Bitacora` (patrón Observer) y `ejecutar`, que repite la Fase 2 con una llamada | carga, limpieza, transformadores |
| `src/medicion.py` | Compara implementaciones en tiempo (`timeit`) y memoria (`tracemalloc`) | — |
| `src/comunicacion.py` | Fase 4: lee las tablas de la Fase 3, verifica su contrato y calcula las cifras que se grafican | — |

Patrones de diseño: **Observer** (la bitácora registra cada paso sin que el paso lo sepa) y **Strategy** (el `Escalador` recibe la forma de escalar como parámetro).

```python
from src.pipeline import construir_pipeline, ejecutar
resultado = ejecutar(RAIZ)                                   # la Fase 2 completa
tubo = construir_pipeline().ajustar(entrenamiento)          # para un modelo: ajustar solo con entrenamiento
prueba_lista = tubo.transformar(prueba)
```

## Cómo ejecutar el proyecto desde cero (Windows, PowerShell)

```
git clone https://github.com/edgararciav-cpu/mcdi500-grupo6.git
cd mcdi500-grupo6
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ipykernel install --user --name mcdi500 --display-name "Python (mcdi500)"
.\.venv\Scripts\python.exe -m jupyter lab
```

En JupyterLab, abrir los notebooks en orden (`F1/F1_Definicion.ipynb`, `F2/F2_Preprocesamiento.ipynb`, `F3/F3_Nucleo_Eficiencia_POO.ipynb` y `F4/F4_Visualizacion_Comunicacion.ipynb`), elegir el kernel **Python (mcdi500)** y ejecutar *Kernel → Restart Kernel and Run All Cells*. En macOS o Linux se usa `.venv/bin/python` en lugar de `.\.venv\Scripts\python.exe`.

Las pruebas se ejecutan con un solo comando desde la raíz del proyecto (unittest viene con Python):

```
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## Resultados (Fase 4)

| Objetivo | Figura | Hallazgo |
|---|---|---|
| 1 y 2 | `F4/figuras/fig1_concentracion_horas.png` | El 10 % de los sitios acumula el 64 % de las horas fuera de servicio por transmisión, y el 20 % acumula el 82 % |
| 3 | `F4/figuras/fig2_enlace_y_proveedor.png` | La fibra de proveedor concentra el 47 % de las fallas, de 13 h cada una; el satelital dura 63 h por falla. Son cifras absolutas: sin el inventario de sitios por tipo de enlace no se comparan tasas |
| 4 | `F4/figuras/fig3_lista_escalamiento.png` | Diez sitios encabezan la lista de escalamiento (`docs/prioridad_escalamiento_f4.csv`). Con pesos iguales entre fallas y minutos coinciden 7 de 10, y SIT_2201, SIT_1174 y SIT_1764 aparecen con cualquier peso (`docs/sensibilidad_prioridad_f4.csv`) |
| 2 | `F4/figuras/fig4_episodios_por_dia.png` | Seis sitios de microondas (SIT_1764 a SIT_1769) fallan los mismos días (15, 21 y 25 de octubre), lo que sugiere un tramo común |

Las cifras exactas de cada hallazgo, con su fuente, están en `docs/hallazgos_f4.csv`, que escribe el notebook F4. F4 también ejecuta las 59 pruebas del proyecto y guarda el registro en `docs/registro_pruebas.txt`; sus 16 controles de validación quedan en `docs/metadatos_fase4.json`.

**Entregables de la Fase 4:** el informe y el video de presentación se entregan en Canvas, en la tarea Sumativa 3. El video está en Canvas Studio y está compartido con el docente.

## Reproducibilidad

- Python 3.14.6 en entorno virtual `.venv`.
- `requirements.txt` declara solo las librerías del proyecto, con versión fija; pip resuelve el resto según el sistema operativo.
- La instalación se prueba en Linux, macOS y Windows con GitHub Actions (`.github/workflows/instalacion.yml`) en cada push.
- Semilla aleatoria: 42. Rutas relativas a la raíz del proyecto (`localizar_raiz`).
- F1 verifica el entorno en su sección 2: se detiene si el kernel no es el del proyecto e informa las versiones que no coincidan.
- F3 comprueba que el pipeline con clases produce los mismos archivos que F2, byte a byte (huella SHA-256); la prueba `test_normal_mismos_archivos_que_la_fase_2` lo repite en cada ejecución de las pruebas.
- F4 recalcula la tabla de recurrencia desde la tabla limpia y comprueba que es idéntica a la de F2 antes de graficar.

## Convención de commits

`docs:` documentación · `data:` datos · `feat:` código nuevo · `fix:` corrección · `test:` pruebas · `perf:` cambio por rendimiento medido. El historial con el detalle de cada commit y el criterio de la rúbrica que respalda está en `docs/bitacora_proceso.md`; el resumen por fase, con las observaciones del docente y su corrección, está en `changelog.md`.

## Uso de herramientas de inteligencia artificial

Se utilizó un asistente de inteligencia artificial generativa como apoyo para explicar conceptos y revisar código. Las decisiones, la ejecución de los notebooks, los commits y la revisión final son del autor.
