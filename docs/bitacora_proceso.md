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

---

## Historial de commits y criterio que respalda cada uno

| Commit | Mensaje | Qué guarda | Producto del enunciado | Criterio de la rúbrica |
|---|---|---|---|---|
| `c7469f7` | docs: crea estructura inicial del proyecto | Carpetas F1 a F4, data, docs, src y scripts; `.gitignore`; README inicial | 2. Repositorio con carpetas F1 y F2 | 8 Repositorio GitHub · 6 Control de versiones |
| `a1e40b8` | data: incorpora incidencias de octubre 2026 anonimizadas en raw | El conjunto de datos de entrada, ya anonimizado | 4. Obtención de datos (F2) | 10 Preprocesamiento (punto de partida) · 5 Reproducibilidad (los datos están en el repo) |
| `b85a209` | docs: agrega bitácora del proceso y script de anonimización | Esta bitácora y el programa que preparó los datos | 5. Evidencias de trazabilidad | 7 Documentación del proceso · 11 Validación (verificación de la anonimización) |
| `e005441` | feat: define el entorno reproducible con requirements.txt | Las 105 dependencias con versión fija | 2. Archivo de dependencias | 5 Reproducibilidad técnica · 4 Herramientas científicas |

Convención de prefijos:

| Prefijo | Uso |
|---|---|
| `docs:` | documentación |
| `data:` | datos |
| `feat:` | algo nuevo que hace funcionar el proyecto |
| `fix:` | corrección |
| `test:` | pruebas |
