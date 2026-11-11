# Fallas recurrentes de transmisión en la red de un operador móvil

Proyecto del curso **MCDI500 · Programación para la Ciencia de Datos** · Magíster en Ciencia de Datos e Inteligencia Artificial, Universidad Andrés Bello.

- **Integrante:** Edgar Arcia Velásquez ([@edgararciav-cpu](https://github.com/edgararciav-cpu)) · Grupo 6 (trabajo individual, informado al docente)
- **Docente:** Dr. Omar Salinas Silva

## Problemática

El NOC registró 21.542 incidencias en octubre de 2026; 588 son fallas de transmisión (enlace de microondas, fibra propia o fibra de proveedor). Varios sitios fallaron más de una vez en el mes, pero no hay una medición que diga cuáles concentran las fallas, cuánto tiempo sin servicio acumulan y qué tipo de enlace las origina. Para el uptime cuentan solo las incidencias con pérdida de servicio: criticidad P1, P2, P3 y P3E (P3 extendida, las que pasan mucho tiempo fuera de servicio).

**Pregunta:** ¿Qué sitios de la red concentran incidencias recurrentes de transmisión (microondas, fibra propia FOP y fibra de proveedor), cuánto tiempo fuera de servicio acumulan y qué tipo de enlace o proveedor las origina, para priorizar su escalamiento y evaluar cambios de transmisión que mejoren el uptime?

**Objetivo general:** Construir un flujo reproducible que transforme el exporte de incidencias en un conjunto limpio y validado, y en una tabla de recurrencia por sitio, apta para priorizar las fallas de transmisión.

**Objetivos específicos:**

1. Convertir la duración (texto h:mm:ss) a minutos, tratar las duraciones inválidas y comparar su distribución y sus atípicos entre las fallas de transmisión y el resto.
2. Clasificar cada falla de transmisión según el tipo de enlace (microondas, fibra propia FOP, fibra de proveedor o satelital) y marcar si afecta el uptime según su criticidad (P1, P2, P3 o P3E).
3. Comparar al menos tres métodos para tratar las duraciones vacías, considerando que corresponden a incidencias aún no normalizadas.
4. Corregir la codificación del texto, unificar las categorías escritas de varias formas y codificar la criticidad y el impacto con orden declarado.
5. Entregar un conjunto validado con pruebas (assert) y una tabla de recurrencia por sitio (fallas con pérdida de servicio y minutos fuera de servicio acumulados), lista para las Fases 3 y 4.

## Datos

- **Origen:** Exporte interno del sistema de tickets del NOC de WOM (operador móvil, Chile). Uso autorizado por escrito por la jefatura; el docente está informado.
- **Período:** 2026-10-01 a 2026-10-31 (cierres hasta 2026-11-10).
- **Archivo:** `data/raw/incidencias_oct2026_anon.csv` (21.542 filas × 49 columnas, separador `;`).
- **Anonimización:** scripts/anonimizar_incidencias.py: personas, tickets de proveedor y códigos de servicio TX reemplazados por códigos; los sitios conservan su mnemónico real (información pública de SUBTEL). El exporte original no forma parte del repositorio.

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
