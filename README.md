# Duración de las incidencias de red de un operador móvil

Proyecto del curso **MCDI500 · Programación para la Ciencia de Datos** · Magíster en Ciencia de Datos e Inteligencia Artificial, Universidad Andrés Bello.

- **Integrante:** Edgar Arcia Velásquez ([@edgararciav-cpu](https://github.com/edgararciav-cpu)) · Grupo 6 (trabajo individual, informado al docente)
- **Docente:** Dr. Omar Salinas Silva

## Problemática

El NOC registró 21.542 incidencias en octubre de 2026. Su duración va de minutos a varios días, y no se sabe con datos qué características se asocian a las más largas.

**Pregunta:** ¿Qué características de una incidencia de red (tipo, criticidad, impacto, región, cantidad de elementos afectados y momento de inicio) se asocian a su tiempo de duración?

**Objetivo general:** Construir un flujo reproducible que transforme el exporte de incidencias en un conjunto limpio y validado, apto para analizar los factores asociados a la duración.

**Objetivos específicos:**

1. Convertir la duración (texto h:mm:ss) a minutos y medir su distribución y sus atípicos por tipo y criticidad.
2. Comparar al menos tres métodos para tratar las duraciones vacías y elegir uno según el cambio en la desviación estándar.
3. Corregir la codificación del texto y unificar las categorías escritas de varias formas.
4. Codificar la criticidad y el impacto con orden declarado y las variables nominales con one-hot.
5. Entregar un conjunto validado con pruebas (assert), listo para las Fases 3 y 4.

## Datos

- **Origen:** Exporte interno del sistema de tickets del NOC de WOM (operador móvil, Chile). Uso autorizado por escrito por la jefatura; el docente está informado.
- **Período:** 2026-10-01 a 2026-10-31 (cierres hasta 2026-11-10).
- **Archivo:** `data/raw/incidencias_oct2026_anon.csv` (21.542 filas × 49 columnas, separador `;`).
- **Anonimización:** scripts/anonimizar_incidencias.py: personas, elementos de red, tickets y códigos TX reemplazados por códigos. El exporte original no forma parte del repositorio.

## Estructura

```
data/raw/        datos de entrada anonimizados (no se modifican)
data/processed/  resultado de la limpieza y transformación (F2)
docs/            diccionario de variables, bitácora, metadatos y vinculación con el mapa
src/             módulo utilidades.py (funciones y clases reutilizables)
scripts/         preparación previa de los datos (anonimización)
F1/ F2/ F3/ F4/  un notebook por fase
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

En JupyterLab, abrir los notebooks en orden (`F1/F1_Definicion.ipynb`, luego `F2/F2_Preprocesamiento.ipynb`), elegir el kernel **Python (mcdi500)** y ejecutar *Kernel → Restart Kernel and Run All Cells*. En macOS o Linux se usa `.venv/bin/python` en lugar de `.\.venv\Scripts\python.exe`.

## Reproducibilidad

- Python 3.14.6 en entorno virtual `.venv`; versiones fijas en `requirements.txt`.
- Semilla aleatoria: 42. Rutas relativas a la raíz del proyecto (`localizar_raiz`).
- Cada notebook verifica el entorno en su primera sección y se detiene si algo no coincide.

## Convención de commits

`docs:` documentación · `data:` datos · `feat:` código nuevo · `fix:` corrección · `test:` pruebas. El historial con el detalle de cada commit y el criterio de la rúbrica que respalda está en `docs/bitacora_proceso.md`.

## Uso de herramientas de inteligencia artificial

Se utilizó un asistente de inteligencia artificial generativa como apoyo para explicar conceptos, revisar código y redactar borradores. Las decisiones, la ejecución y la revisión final son del autor.
