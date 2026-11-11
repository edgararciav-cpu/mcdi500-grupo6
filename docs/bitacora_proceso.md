# Bitácora del proceso · Sumativa 1 (Fases 1 y 2)

Un registro por paso, en el orden en que se hizo. Cada registro dice qué pide la actividad, qué se hizo, qué resultado salió y con qué comandos. Este archivo va al repositorio en `docs/` y es la evidencia de los criterios 7 (documentación del proceso) y 14 (vinculación con el mapa).

---

## Paso 1 · Leer la rúbrica y la guía (10-11-2026)

- **Qué pide:** el profesor recomienda abrir la rúbrica al empezar, no al terminar (presentación de la Semana 1, lámina 7).
- **Qué se hizo:** se leyeron la rúbrica de Canvas, la guía de desarrollo de la Sumativa 1 y la presentación de la Semana 1.
- **Resultado:** 15 criterios y 99 puntos. Según el profesor, cerca de dos tercios están en los notebooks, el código y el repositorio.

## Paso 2 · Descargar la plantilla institucional (10-11-2026)

- **Qué pide:** el informe va en el entregable institucional (enunciado, "Aspectos formales").
- **Qué se hizo:** se descargó `f1_s01_evaluacion_entregable.docx` desde el enlace del enunciado en Canvas. Se le consultó al profesor porque la plantilla dice "Fase 1" y no trae los apartados V ni VII.
- **Resultado:** el profesor indicó usarla solo para el formato, seguir los apartados I a IX del enunciado y titular la portada "Sumativa 1: Fases 1 y 2".

## Paso 3 · Elegir el conjunto de datos (10-11-2026)

- **Qué pide:** al menos 2.000 filas, 12 columnas y 3 roles analíticos; de los últimos 5 años; sin datos personales; fuente verificable con permiso de uso (anuncio del 03-11).
- **Qué se hizo:** se compararon dos exportes internos de WOM, una base de celdas 5G y las incidencias del NOC de octubre de 2026, usando el validador del curso.
- **Resultado:** las dos cumplen. Se eligieron las **incidencias** (21.542 filas × 49 columnas) porque traen más que limpiar:
  - 24,7 % de duraciones vacías;
  - tildes rotas en unas 20 mil celdas;
  - la misma categoría escrita de cinco formas (`NA`, `N/A`, `na`, `no aplica`, `No aplica`);
  - una criticidad ordinal (P1 a P4).
- **Comando:**
  ```
  python validar_dataset.py Export_Incidencias_Octubre2026.csv --sep ";" --encoding utf-8-sig
  ```
  - `python` ejecuta un programa escrito en Python.
  - `validar_dataset.py` es el programa del profesor que revisa los requisitos.
  - `--sep ";"` le avisa que las columnas vienen separadas por punto y coma.
  - `--encoding utf-8-sig` le dice cómo están guardadas las letras.

## Paso 4 · Anonimizar (11-11-2026, 04:45)

- **Qué pide:** "sin datos personales identificables" (requisitos del conjunto de datos).
- **Qué se hace:** `anonimizar_incidencias.py` reemplaza por códigos:
  - los nombres de personas: `Incident Manager` → IM_01 y `Creador de TT` → OP_01;
  - los elementos de red (NE_0001), los tickets de proveedor y los códigos TX que tienen número.

  No toca nada más, para que la limpieza quede en la Fase 2. `Código de Servicio` se mantiene: son códigos de suministro eléctrico, no RUT.
- **Autoría:** el programa se escribió con asistencia de IA (se declara en el informe) y fue revisado y ejecutado por el autor.
- **Resultado obtenido:**

  | Columna | Valores distintos reemplazados | Código |
  |---|---|---|
  | Incident Manager | 8 | IM_ |
  | Creador de TT | 36 | OP_ |
  | Network Element | 3.452 | NE_ |
  | Ticket de proveedor (con número) | 266 | TKP_ |
  | Código servicio TX 1 a 5 (con número) | 149 | TXS_ |

  Hubo 7.503 reemplazos dentro de Titulo y Detalle. El programa terminó con "Verificación: OK, no queda ningún valor original".
- **Enfoque descartado (primera versión, 10-11):** al principio se buscaban todos los valores codificados en todas las columnas. Al revisar el resultado aparecieron cambios en columnas que no debían tocarse, como `Estado`, `Proveedor` y `TT`. La causa: algunos "tickets de proveedor" y "códigos TX" no son códigos sino palabras como `Pendiente` o `ENEL`. Se corrigió en tres puntos:
  1. tickets y códigos TX se codifican solo si tienen números;
  2. la búsqueda en texto libre se limita a `Titulo` y `Detalle`;
  3. solo se buscan nombres de personas y de elementos de red, como palabra completa.

  **Impacto:** se mantienen los marcadores `N/A`, `NA` y `Pendiente`, que se tratan en la Fase 2.
- **Comprobación independiente:** se comparó con pandas contra el original. Salieron las mismas 21.542 filas × 49 columnas, en el mismo orden. Solo cambiaron las 11 columnas previstas, quedan 0 nombres de personas, y se mantienen los TT y los vacíos de duración.
- **Comandos (PowerShell):**
  ```
  cd C:\Users\edgar\MCDI500\preparacion
  python anonimizar_incidencias.py "C:\Users\edgar\Downloads\Export_Incidencias_Octubre2026.csv" incidencias_oct2026_anon.csv
  ```
  - `cd` (change directory) entra a la carpeta donde está el programa.
  - La segunda línea ejecuta el programa con dos datos: el archivo de origen y el nombre del archivo nuevo.

## Paso 5 · Guardar como CSV UTF-8 (11-11-2026)

- Lo hizo el mismo programa del paso 4: `incidencias_oct2026_anon.csv`, en UTF-8, con `;` como separador (5,8 MB). Va a `data/raw/` del repositorio. El exporte original de WOM no se sube.

## Paso 6 · Informar al profesor (10-11-2026)

- **Qué se hizo:** el profesor ya sabe que el trabajo es individual (Grupo 6) y que se usan datos internos de WOM.
- **Resultado:** respondió por correo el 10-11 con orientaciones para la entrega:
  - usar la plantilla solo para el formato;
  - seguir los apartados I a IX;
  - commits pequeños con una sola identidad;
  - coherencia entre el informe y el repositorio;
  - probar el README desde cero antes de entregar.

## Paso 8 · Crear el repositorio (11-11-2026, 05:29)

- **Qué pide:** "repositorio GitHub actualizado, con carpetas F1 y F2, estructura organizada, README técnico, archivo de dependencias e historial de commits" (enunciado, producto 2).
- **Qué se hizo:** se creó `edgararciav-cpu/mcdi500-grupo6`, público y vacío, en github.com/new. Se configuró la identidad de Git una sola vez y se clonó el repositorio.
- **Comandos (PowerShell):**
  ```
  git config --global user.name "Edgar Arcia"
  git config --global user.email "edgararciav@gmail.com"
  git config --global init.defaultBranch main
  cd C:\Users\edgar\MCDI500
  git clone https://github.com/edgararciav-cpu/mcdi500-grupo6.git
  ```
  - `git config --global` fija el nombre y el correo que firman cada commit. Es el mismo correo de la cuenta de GitHub, para que todos los commits salgan con una sola identidad.
  - `git clone` descarga el repositorio y lo deja conectado con GitHub.

## Paso 9 y 10 · Estructura inicial y primer commit (11-11-2026, 05:43)

- **Qué se hizo:** carpetas `F1` a `F4`, `data/raw`, `data/processed`, `docs`, `src` y `scripts`, igual al proyecto modelo. Se agregaron un `.gitignore` (excluye `.venv` y el exporte original de WOM) y un README inicial.
- **Resultado:** commit `c7469f7` "docs: crea estructura inicial del proyecto". GitHub lo reconoce como `edgararciav-cpu`.
- **Comandos:**
  ```
  git add .
  git commit -m "docs: crea estructura inicial del proyecto"
  git push -u origin main
  ```
  - `git add .` prepara todos los archivos nuevos.
  - `git commit -m` guarda una versión con su mensaje (prefijo `docs:` según la convención).
  - `git push -u origin main` la sube a GitHub y deja vinculada la rama local con la remota.

## Pasos 11 a 13 · Entorno reproducible (11-11-2026)

- **Qué pide:** criterio 5, reproducibilidad técnica (6 pts): "ambientes virtuales y dependencias de forma completa, verifican la correcta instalación de cada componente".
- **Qué se hizo:** se creó el entorno virtual, se instalaron las librerías del proyecto, se fijaron sus versiones y se registró el kernel de Jupyter.
- **Resultado:** `.venv` con Python 3.14.6 y `requirements.txt` con 105 paquetes con versión exacta: pandas 3.1.1, numpy 2.5.4, scikit-learn 1.9.1, matplotlib 3.11.2, jupyterlab 4.6.6 e ipykernel 7.4.0. El kernel "Python (mcdi500)" quedó registrado. Los imports se verificaron sin errores.
- **Incidencia y corrección:** la primera vez los comandos se ejecutaron desde `C:\Users\edgar` y no desde el proyecto, así que PowerShell no encontró `.venv`. Se corrigió entrando primero a la carpeta con `cd`.
- **Comandos (PowerShell, desde la carpeta del proyecto):**
  ```
  python -m venv .venv
  .\.venv\Scripts\python.exe -m pip install --upgrade pip
  .\.venv\Scripts\python.exe -m pip install jupyterlab ipykernel numpy pandas matplotlib scikit-learn
  .\.venv\Scripts\python.exe -m pip freeze | Set-Content -Encoding ascii requirements.txt
  .\.venv\Scripts\python.exe -m ipykernel install --user --name mcdi500 --display-name "Python (mcdi500)"
  ```
  - `python -m venv .venv` crea un Python propio del proyecto, aislado del resto del computador.
  - `.\.venv\Scripts\python.exe` usa ese Python sin "activarlo". En PowerShell, la activación suele quedar bloqueada por la política de ejecución de scripts.
  - `pip install` instala las librerías y `pip freeze` lista cada una con su versión exacta. El resultado se guarda en `requirements.txt` para reconstruir el mismo entorno en otro equipo con `pip install -r requirements.txt`.
  - `ipykernel install` registra el kernel. Así los notebooks se ejecutan con el Python del proyecto y no con el del sistema.

## Paso 14 · Módulo propio `src/utilidades.py` (11-11-2026, 07:00)

- **Qué pide:** criterio 9 (codificación con funciones, parámetros y docstring) y modularidad o POO.
- **Qué se hizo:** un módulo con 4 funciones (`reparar_texto`, `normalizar_nombre`, `normalizar_columnas` y `duracion_a_minutos`), la clase `ConjuntoDatos` (con `existe`, `cargar` y `resumen`) y la excepción propia `ProyectoError`.
- **Resultado:** commit `9f9d7f5`. Las pruebas normal, límite y excepción están en la sección 4.1 del notebook F1.

## Paso 15 · Validación del conjunto con el programa del curso (11-11-2026, 07:03)

- **Qué pide:** paso 3 de la lámina 67, validar el conjunto con `validar_dataset.py`.
- **Resultado:** `docs/validacion_dataset.md` dice CUMPLE (21.542 × 49). Commit `e6e738d`.

## Paso 16 · Notebook F1 ejecutado (11-11-2026, 07:20)

- **Qué se hizo:** `F1/F1_Definicion.ipynb` con 11 secciones, igual al modelo del docente: definición, entorno, estructura, módulo, ficha y diccionario, control de versiones, validación, vinculación con el mapa, persistencia, conclusiones y verificación.
- **Resultado:** ejecutado con *Restart & Run All*, numeración continua, 0 errores, 0 advertencias y "Fase 1 validada: 8 de 8". Commit `abd3693`.

## Paso 17 · Cambio de la pregunta al foco en transmisión (11-11-2026)

- **Qué cambió:** la pregunta original buscaba qué características de una incidencia se asocian a su duración. La nueva pregunta busca **qué elementos de red concentran fallas recurrentes de transmisión** (microondas, fibra propia FOP y fibra de proveedor), cuánto tiempo fuera de servicio acumulan y qué tipo de enlace o proveedor las origina.
- **Motivo:** es la decisión que el NOC necesita tomar en la operación. Si un sitio falla varias veces por transmisión, se escala con el área que corresponde (transmisión propia o el proveedor) para evaluar un cambio de transmisión y asegurar el uptime. La pregunta anterior era más amplia y no llevaba a una acción concreta.
- **Evidencia de que la pregunta tiene datos** (sección 5.5 del notebook F1):
  - 588 fallas de transmisión de 21.542 (Tx Proveedor 333 y Tx Propia 255);
  - 337 elementos de red con al menos una falla, 134 con 2 o más y 46 con 3 o más; uno falló 19 veces;
  - subtipos principales: corte de fibra de proveedor 214, pérdida de enlace MW 135, pérdida de redundancia 100 y corte de fibra FOP 72.
- **Impacto:**
  - se reescribieron la pregunta, el objetivo general, los 5 objetivos específicos, el alcance, una restricción y un supuesto;
  - las 21.542 filas se siguen limpiando completas, y el análisis se enfoca en las 588 de transmisión;
  - la Fase 2 suma dos productos: la clasificación por tipo de enlace y la tabla de recurrencia por elemento de red con sus minutos acumulados;
  - en la clasificación aparece un cuarto tipo que no estaba previsto: 15 fallas de **módem satelital** (Tx Proveedor). La Fase 2 lo trata como una categoría propia.
- **Fuera del alcance:** la decisión de cambiar la transmisión de un sitio y sus costos. El proyecto entrega la priorización y la decisión la toman las áreas de transmisión.
- **Ajuste por criticidad (definición operativa del NOC):** solo P1, P2, P3 y P3E (P3 extendida, las que pasan mucho tiempo fuera de servicio) son pérdida de servicio y afectan el uptime. P2 Redundancia, P2R y P4 no.
  - De 588 fallas de transmisión, 264 dejaron el servicio caído: 206 elementos, 35 con 2 o más pérdidas y 12 con 3 o más; el máximo es 11.
  - El elemento con más fallas de transmisión (19) tiene solo 1 con pérdida de servicio. Sin este filtro se habría priorizado mal.
  - La mediana de la P3E es 3.188 minutos (unas 53 horas), contra 247 de la P3.
  - La tabla de recurrencia de la Fase 2 se construye solo con las fallas con pérdida de servicio.
- **Hallazgo nuevo para la Fase 2:** 2 duraciones negativas (`-498136:-36:-45` y `-497906:-41:00`) en incidencias cerradas P4. Se cuentan en la sección 5.3 y se tratan en la Fase 2.
- **Incidencia de los commits `348231e` y `376d53d`:** los dos guardaron el notebook sin las salidas, porque el commit se hizo antes de ejecutarlo y guardarlo. Se corrigió en el commit siguiente. **Orden correcto:** ejecutar (*Restart & Run All*), guardar (Ctrl+S) y recién ahí `git add` y `git commit`.

---

## Historial de commits y criterio que respalda cada uno

| Commit | Mensaje | Qué guarda | Producto del enunciado | Criterio de la rúbrica |
|---|---|---|---|---|
| `c7469f7` | docs: crea estructura inicial del proyecto | Carpetas F1 a F4, data, docs, src y scripts; `.gitignore`; README inicial | 2. Repositorio con carpetas F1 y F2 | 8 Repositorio GitHub · 6 Control de versiones |
| `a1e40b8` | data: incorpora incidencias de octubre 2026 anonimizadas en raw | El conjunto de datos de entrada, ya anonimizado | 4. Obtención de datos (F2) | 10 Preprocesamiento (punto de partida) · 5 Reproducibilidad (los datos están en el repo) |
| `b85a209` | docs: agrega bitácora del proceso y script de anonimización | Esta bitácora y el programa que preparó los datos | 5. Evidencias de trazabilidad | 7 Documentación del proceso · 11 Validación (verificación de la anonimización) |
| `e005441` | feat: define el entorno reproducible con requirements.txt | Las 105 dependencias con versión fija | 2. Archivo de dependencias | 5 Reproducibilidad técnica · 4 Herramientas científicas |
| `cfceefa` | docs: registra el entorno reproducible y la relación de cada commit con la rúbrica | Pasos 11 a 13 de esta bitácora y esta tabla | 5. Evidencias de trazabilidad | 7 Documentación del proceso · 6 Control de versiones |
| `9f9d7f5` | feat: agrega módulo utilidades con funciones, clase y excepción propia | `src/utilidades.py` | 3. Notebook F1 (código modular) | 9 Codificación · 12 Notebook F1 |
| `e6e738d` | data: valida el conjunto con validar_dataset.py del curso | `validar_dataset.py` y `docs/validacion_dataset.md` | 4. Obtención de datos | 11 Validación · 3 Problemática (requisitos del dataset) |
| `abd3693` | feat: notebook F1 con definición, entorno, ficha, diccionario y validación | Notebook F1, README generado y productos de `docs/` | 3. Notebook F1 | 12 Notebook F1 · 3 Problemática · 5 Reproducibilidad · 14 Vinculación con el mapa |
| `348231e` | docs: ajusta la problemática al foco en fallas de transmisión | Pregunta, objetivos y alcance nuevos; sección 5.5; README y bitácora | 1. Informe (problemática) · 3. Notebook F1 | 3 Problemática · 7 Documentación del proceso |
| `376d53d` | docs: define el uptime por criticidad y guarda la ejecución de F1 | Criticidades que afectan el uptime y duraciones inválidas (el notebook quedó sin salidas) | 3. Notebook F1 · 5. Evidencias | 3 Problemática · 11 Validación |
| (siguiente) | fix: guarda las salidas de la ejecución del notebook F1 | Notebook F1 ejecutado: numeración 1 a 22, 0 errores, 8 de 8 | 3. Notebook F1 | 12 Notebook F1 · 5 Reproducibilidad |

Convención de prefijos:

| Prefijo | Uso |
|---|---|
| `docs:` | documentación |
| `data:` | datos |
| `feat:` | algo nuevo que hace funcionar el proyecto |
| `fix:` | corrección |
| `test:` | pruebas |
