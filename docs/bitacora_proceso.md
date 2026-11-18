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

## Pasos 9 y 10 · Estructura inicial y primer commit (11-11-2026, 05:43)

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
- **Resultado:** commit `70a2144`. Las pruebas normal, límite y excepción están en la sección 4.1 del notebook F1.

## Paso 15 · Validación del conjunto con el programa del curso (11-11-2026, 07:03)

- **Qué pide:** paso 3 de la lámina 67, validar el conjunto con `validar_dataset.py`.
- **Resultado:** `docs/validacion_dataset.md` dice CUMPLE (21.542 × 49). Commit `d33287c`.

## Paso 16 · Notebook F1 ejecutado (11-11-2026, 07:20)

- **Qué se hizo:** `F1/F1_Definicion.ipynb` con 11 secciones, igual al modelo del docente: definición, entorno, estructura, módulo, ficha y diccionario, control de versiones, validación, vinculación con el mapa, persistencia, conclusiones y verificación.
- **Resultado:** ejecutado con *Restart & Run All*, numeración continua, 0 errores, 0 advertencias y "Fase 1 validada: 8 de 8". Commit `7ab07a0`.

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
- **Incidencia de los commits `97b3766` y `a01920f` (ver paso 18 para la Fase 2):** los dos guardaron el notebook sin las salidas, porque el commit se hizo antes de ejecutarlo y guardarlo. Se corrigió en el commit siguiente. **Orden correcto:** ejecutar (*Restart & Run All*), guardar (Ctrl+S) y recién ahí `git add` y `git commit`.

## Paso 18 · Pipeline de la Fase 2 en la rama `f2-pipeline` (11-11-2026)

- **Qué pide:** criterios 9, 10, 11 y 13 (codificación, preprocesamiento, validación y notebook F2) y el uso de ramas del criterio 6.
- **Qué se hizo:** `F2/F2_Preprocesamiento.ipynb` con el flujo obtener → explorar → limpiar → transformar → escalar → validar → guardar, en una rama propia que se integra a `main` con un pull request. Cada decisión queda con su cifra en `docs/bitacora_decisiones.md`, que genera el mismo notebook.
- **Resultado:**
  - 43.811 celdas con tildes rotas pasan a 0, y 29.667 marcadores de "sin dato" pasan a vacío;
  - las columnas bajan de 49 a 29 y no se pierde ninguna fila;
  - se comparan 4 métodos para las duraciones vacías;
  - criticidad e impacto quedan con orden declarado, y hay one-hot y 3 escaladores comparados;
  - la tabla de recurrencia tiene 203 elementos con pérdida de servicio por transmisión: 34 con 2 o más fallas y 12 con 3 o más (cifra reemplazada en el paso 19 por el conteo por sitio);
  - 15 de 15 reglas de integridad cumplidas y pruebas normal, límite y excepción en 9 funciones.
- **Función recursiva (RA2):** `utilidades.fusionar_intervalos` une las caídas de un mismo elemento que se traslapan, para no contar dos veces el tiempo fuera de servicio.
- **Incidencia y corrección:** al validar apareció que `reparar_texto` no arreglaba la Ñ (`Ã‘uÃ±oa`). Esa letra se rompió con la codificación de Windows (cp1252), no con latin-1. Se corrigió la función para probar cp1252 primero, y quedan 0 celdas rotas.
- **Otra corrección:** el one-hot con frecuencia mínima de 1 % agrupaba microondas y FOP como poco frecuentes, y son el foco de la pregunta. El tipo de enlace se codifica sin agrupar.
- **Orden de trabajo, para no repetir la incidencia del paso 17:** ejecutar, guardar con Ctrl+S y recién ahí `git add` y `git commit`.

## Paso 19 · Mnemónicos reales, conteo por sitio y reglas del NOC (11-11-2026)

- **Qué cambió y por qué:** al revisar el gráfico de la Fase 2, los sitios aparecían como `NE_0132`, y así no se puede saber qué sitio escalar. Los mnemónicos de los sitios no son datos personales y la SUBTEL ya los publica. Por eso el anonimizador dejó de codificarlos, y ahora todo el proyecto usa el nombre real. Las personas siguen codificadas (IM_, OP_), igual que los tickets de proveedor y los códigos de servicio TX.
- **Hallazgo al usar los nombres reales:** `Network Element` puede traer **varios sitios en la misma celda**, separados por dos espacios. Un espacio simple es parte del nombre del sitio (hoy cada sitio es un código, como `SIT_0304`, que no lleva espacios). Separar por dos espacios coincide con `Q Network Element` en las 21.542 filas. Hay 1.098 incidencias con más de un sitio.
  - Antes se contaban como un solo "elemento" y la tabla mostraba 203. Contando por sitio, son **559 sitios** con pérdida de servicio por transmisión: 149 con 2 o más fallas y 21 con 3 o más.
  - Se agregó `utilidades.separar_sitios`, con pruebas.
- **Reglas del NOC confirmadas por Edgar:**
  - **Criticidad:** P1 afecta a más de 50.000 clientes, P2 a más de 30.000, y P3 y P3E a menos de 30.000. La P3E es una P3 que dura más de 24 horas.
  - **Pérdida de servicio:** P1, P2, P3 y P3E tienen pérdida de servicio. P2 Redundancia y P2R no, porque la redundancia está activa.
  - **Orden ordinal:** P4 < P2 Redundancia < P2R Degradación < P3 = P3E < P2 < P1. P3 y P3E comparten nivel, y la duración las distingue con la bandera `es_extendida`.
  - **Satelital:** el proveedor es TGS Starlink. El exporte lo deja vacío en las 15 fallas satelitales.
- **Corrección de enfoque:** antes de esto se habían supuesto dos reglas del negocio, el proveedor satelital como "Sin dato" y la P3E como menos grave que la P2 Redundancia. Desde ahora toda regla del NOC se consulta antes de aplicarla.
- **Incidencia repetida:** los commits `862650d` y `954d6f4` volvieron a guardar los notebooks sin salidas, porque se hicieron antes de ejecutarlos en Jupyter. Desde aquí se revisa en el disco que los notebooks tengan la numeración completa **antes** de cada commit. Se corrigió en el commit `fix:` siguiente.
- **Impacto en el repositorio:** se regeneró `data/raw/incidencias_oct2026_anon.csv` con el anonimizador ajustado y se volvió a correr `validar_dataset.py`, que sigue diciendo CUMPLE. F1 y F2 se ejecutaron de nuevo, y la tabla de recurrencia ahora es `recurrencia_tx_por_sitio.csv`. F1 da 8 de 8 y F2 da 17 de 17 reglas de integridad.

## Paso 20 · Mapa conceptual (11-11-2026)

- **Qué pide:** criterio 14, con los seis tipos de elemento del mapa (herramientas, procesos, flujo reproducible, decisiones técnicas, organización del repositorio y estructura del notebook), conectores con verbo y leyenda. El curso también pide distinguir lo implementado de lo proyectado.
- **Qué se hizo:** `scripts/mapa_conceptual.py` dibuja el mapa en `docs/figuras/mapa_conceptual.png`. Cada tipo tiene su color; el borde continuo marca lo implementado en F1 y F2 y el borde punteado lo proyectado para F3 y F4. Al ser un programa, el mapa se actualiza en cada fase con un comando.
- **Enfoque descartado:** la primera versión ubicaba las cajas sin una grilla, y las flechas cruzaban otras cajas y las etiquetas se superponían. Se reordenó en cinco columnas para que cada flecha vaya a una caja vecina, y las flechas parten del borde de cada caja.
- **Comando:**
  ```
  .\.venv\Scripts\python.exe scripts\mapa_conceptual.py
  ```

## Paso 21 · Prueba desde cero (11-11-2026, 10:54)

- **Qué pide:** el docente recomienda clonar el repositorio en otra carpeta y seguir el README desde cero antes de entregar. Es la evidencia del criterio 5: estabilidad en cualquier equipo.
- **Qué se hizo:** se clonó `main` (merge `eca9340`) en `C:\Users\edgar\MCDI500\prueba-desde-cero`, con un entorno virtual nuevo instalado desde `requirements.txt`, y se ejecutaron F1 y F2 completos.
- **Resultado:**
  - F1: 0 errores, 0 advertencias y "Fase 1 validada: 8 de 8".
  - F2: 0 errores, 0 advertencias y "17 de 17 reglas de integridad".
  - Los tres archivos de `data/processed` del clon tienen la **misma huella SHA-256** que los del repositorio: el resultado es idéntico byte a byte.
- **Incidencia y corrección:** al registrar el kernel desde el clon, la definición «Python (mcdi500)» quedó apuntando al entorno del clon. Se volvió a registrar desde el proyecto original con el mismo comando.
- **Comandos:** los del README, sección "Cómo ejecutar el proyecto desde cero".

## Paso 22 · Restricciones nuevas y uptime solo con minutos de octubre (11-11-2026, tarde)

- **Qué cambió y por qué:** en la revisión final del informe se vio que dos de las restricciones no eran límites del análisis (cómo se codifican las personas y de dónde sale el nemónico de los sitios). Se reemplazaron por límites reales de los datos, verificados en el archivo:
  - el exporte no informa cuántos clientes afectó cada incidencia: solo se conoce el rango que fija la criticidad (ninguna de las 49 columnas trae clientes);
  - el tipo de enlace no viene en una columna: se obtiene del texto de la incidencia NOC (MW = microondas, FOP = fibra propia).
- **Regla del NOC (definida por Edgar):** el uptime es mensual, así que para octubre **solo cuentan los minutos de octubre**. Todas las incidencias del archivo empiezan en octubre, pero 288 se normalizaron en noviembre (la última, el 10-11 a las 11:33). De ellas, 6 son de transmisión con pérdida de servicio.
- **Enfoque descartado:** contar la duración completa de esas 6 caídas. Era más simple y no tocaba el pipeline, pero sumaba al uptime de octubre tiempo que pertenece a noviembre.
- **Cómo se implementó:** en la sección 4.4 de F2, el cierre se corta al 31-10 a las 23:59 (`FIN_OCTUBRE`) antes de fusionar los intervalos. La columna `duracion_min` del conjunto limpio conserva la duración completa, porque describe la incidencia.
- **Impacto medido:** 19.029 minutos de noviembre dejan de contarse en 6 sitios. SIT_2201, el sitio con más horas fuera de servicio, baja de 725 a 660 horas. La cantidad de sitios (559) y de sitios con 2 o más fallas (149) no cambia.
- **Verificación:** antes de pasarlo al repositorio, F1 y F2 se ejecutaron completos en una copia: 8 de 8 y 17 de 17, sin errores ni advertencias.

## Paso 23 · Correcciones de la auditoría independiente (11-11-2026, tarde)

- **Qué se hizo:** antes de entregar, un revisor independiente recorrió los 15 criterios de la rúbrica y comparó cada cifra del informe con los notebooks, `docs/`, `data/processed/` y `git log`. Además clonó el repositorio desde GitHub (commit `663037e`), ejecutó F1 y F2 y obtuvo los tres archivos de `data/processed` idénticos byte a byte.
- **Lo que se corrigió:**
  - **Duración de la transmisión:** el informe decía que las fallas de transmisión son las que más duran, y no es así: tipos como Hardware o Sitio Vandalizado tienen medianas mayores. Ahora dice que su mediana supera las 10 horas (605 min) frente al resto, y la tabla de atípicos de F2 (sección 2.4) muestra la mediana de cada grupo para que la cifra se pueda verificar.
  - **P3E:** se quitó la definición "P3 que dura más de 24 h", que no calzaba con la duración de la incidencia (112 de 674 P3E duran 24 h o menos). Regla del NOC confirmada por Edgar: la P3E se trata igual que una P3.
  - **Duraciones negativas:** F2 atribuía las 2 a una fecha de cierre `0000-00-00`; en realidad son incidencias cerradas **sin** fecha de cierre (los `0000-00-00` están en otras filas, con duraciones válidas).
  - **Declaración de IA:** el README y F1 decían otra cosa que el informe; ahora los tres usan el mismo texto.
  - **Mapa conceptual:** la caja de uptime dice "solo octubre", y la tabla de vinculación del informe tiene solo elementos que están en el mapa.
  - **Consistencia:** "nemónico" en todo el proyecto; la bitácora de decisiones dice cp1252, igual que el paso 18; las listas de verificación de F1 y F2 quedan marcadas; la tabla de commits de esta bitácora muestra el hash de cada commit.
- **Lo que no se cambia:** todo el historial es del 11-11 (no se reescribe la historia para repartirlo) y los mensajes de commits antiguos dicen "mnemónicos".

# Fase 3 · Sumativa 2

## Paso 24 · Repositorio privado y dependencias solo del proyecto (13 al 15-11-2026)

- **Retroalimentación de la Sumativa 1 (93 de 99):** el profesor pidió cinco correcciones para la Fase 3:
  - resolver la publicación de los datos;
  - objetivos analíticos;
  - dependencias que se instalen en cualquier sistema;
  - commits repartidos en la semana;
  - declarar la limitación de las duraciones imputadas.
- **Datos del operador:** el repositorio quedó **privado** el 13-11 y se compartirá con el docente. El 15-11 se decidió cambiar los sitios por códigos y limpiar el historial (paso 25).
- **Dependencias.** Antes, `requirements.txt` era un volcado de 105 paquetes (`pip freeze`) con `pywinpty`, que solo existe en Windows, así que la instalación fallaba en macOS y Linux. Ahora declara solo las 6 librerías que el proyecto importa o usa para ejecutar los notebooks (pandas, NumPy, scikit-learn, matplotlib, JupyterLab e ipykernel), con versión fija. Las dependencias de esas librerías las resuelve pip según el sistema.
- **Cómo se verificó:**
  - `uv pip compile` resolvió el archivo para Linux (x86_64), macOS (arm64) y Windows solo con paquetes compilados. `pywinpty` aparece únicamente en Windows.
  - Se agregó `.github/workflows/instalacion.yml`: en cada push, GitHub instala `requirements.txt` en Ubuntu, macOS y Windows y compara las versiones importadas con las declaradas.
- **F1, sección 2** (se aplica en el paso 25, cuando se vuelven a ejecutar los notebooks):
  - lee `requirements.txt` sin contar los comentarios;
  - comprueba que la lista verificada sea la misma que la declarada;
  - si una versión no coincide, **informa la diferencia y sigue**, para que se pueda revisar el resto del notebook (pedido del profesor);
  - solo se detiene si el kernel no es el del proyecto.

  Probado en una copia: 6 librerías con la versión declarada y "8 de 8". El F1 actual también funciona con el archivo nuevo, porque sus 6 librerías clave están declaradas.
- **Enfoque descartado:** generar `requirements.txt` con `pip freeze`. Fija también las dependencias propias de cada sistema operativo, y por eso no se puede instalar en otro.
- **Integración:** rama `f3-dependencias` (commits `0676823`, `52efc82` y `e36b384`), integrada a `main` con el pull request #1 (`00a152e`). Las verificaciones de GitHub Actions pasaron en Ubuntu, macOS y Windows.

## Paso 25 · Sitios con código, texto libre omitido e historial limpio (15-11-2026)

- **Qué pidió el profesor:** el repositorio publicaba datos operativos internos del operador, con los identificadores reales de los sitios. Había que adjuntar una autorización escrita o reemplazar los sitios por códigos y limpiar el historial. Edgar decidió codificar sin esperar la autorización.
- **Anonimizador** (`scripts/anonimizar_incidencias.py`):
  - cada sitio de `Network Element` pasa a un código `SIT_0001`, `SIT_0002`…, en orden de aparición (3.879 sitios). En las celdas con varios sitios, cada uno recibe su código y se conservan los separadores de dos espacios;
  - `Titulo` y `Detalle` pasan a «[texto omitido]», porque nombraban sitios, equipos (routers, radios) y tickets de terceros. Las celdas vacías y los marcadores de vacío se conservan, para que la medición de vacíos no cambie;
  - la tabla de equivalencias sitio → código **no** está en el repositorio: el script la escribe solo si se le pasa una ruta, y queda en la carpeta local de preparación, para uso interno del NOC.
- **Verificación del anonimizador:** con el exporte original solo cambian esas 3 columnas; las otras 46 son idénticas. La cantidad de sitios por celda coincide en las 21.542 filas, y la búsqueda final no encuentra ningún sitio real.
- **Efecto en los resultados:** ninguno en el análisis. Siguen 559 sitios, 149 con 2 o más fallas, 21 con 3 o más, 19.029 minutos de noviembre descontados, "8 de 8" en F1 y "17 de 17" en F2. Solo cambian las celdas con tildes rotas, que bajan de 43.811 a 43.634, porque `Detalle` tenía muchas.
- **Historial limpio:** se reescribieron los 31 commits con `git filter-repo`:
  - en todas las versiones, los datos quedan con códigos;
  - los notebooks antiguos pierden sus salidas, que mostraban sitios y texto libre;
  - en los demás archivos, cada nombre real pasa a su código.

  Las fechas, el autor y los mensajes se conservan. Se revisaron los 86 objetos del historial nuevo: 0 nombres reales, 0 fragmentos del texto libre original y 0 nombres de equipos. El repositorio de GitHub se borró y se creó de nuevo, porque el pull request de la Fase 2 seguía guardando los commits antiguos y esas referencias no se pueden borrar con un push.
- **Hashes nuevos:** la reescritura cambió 30 de los 31 hashes; solo el primer commit (`c7469f7`) conserva el suyo. En esta bitácora ya están actualizados. `docs/equivalencia_commits_reescritura.csv` da la equivalencia, para leer el informe de la Sumativa 1, que cita los hashes antiguos.
- **Código y textos:**
  - `utilidades.separar_sitios` documenta su ejemplo con códigos y prueba el caso del espacio simple con un nombre ficticio («SITIO NORTE»);
  - F1 y F2 describen los sitios como códigos;
  - el mapa conceptual agrega la decisión técnica «Datos del operador: sitios con código y repo privado», que exige la anonimización (sugerencia del profesor).
- **F1** se vuelve a ejecutar con la verificación de versiones del paso 24, que informa las diferencias sin detenerse.
- **Enfoque descartado:**
  - **codificar los sitios dentro del texto libre:** el texto también traía nombres de equipos y tickets de terceros que una lista de sitios no detecta;
  - **force push sin borrar el repositorio:** dejaba los commits antiguos accesibles desde el pull request #1.

## Paso 26 · Núcleo de la Fase 3: código en `src/`, clases, pipeline, eficiencia y pruebas (16-11-2026)

- **Qué pidió el profesor (guía ilustrada del 13-11):** pasar el código de F2 a `src/`, crear clases solo donde se aprende de los datos, armar un pipeline con uno o dos patrones justificados, demostrar que el resultado es idéntico al de F2, comparar implementaciones con `timeit` y `tracemalloc`, y dejar pruebas en `tests/` que corran con un comando. Todo en la rama `f3-nucleo`.
- **Código en `src/`:** `carga.py` (lee y verifica `data/raw`), `limpieza.py` (16 funciones que no aprenden nada), `transformadores.py` (clase base y clases que aprenden), `pipeline.py` (los 15 pasos de F2 en el mismo orden) y `medicion.py`.
- **Clases solo donde se aprende:** `UnificadorVariantes`, `EliminadorCasiVacias`, `ImputadorMedianaGrupo`, `CodificadorNominal` y `Escalador` guardan lo aprendido en `_parametros` y lo aplican a cualquier conjunto. Las funciones sin estado se envuelven con `PasoFijo` para que el pipeline las recorra igual (polimorfismo) sin convertirlas en clases artificiales.
- **Patrones:** Observer (`Bitacora`, registra filas y columnas de cada paso) y Strategy (`Escalador` con `estandar`, `minmax` o `robusta`).
- **Equivalencia con F2:** `ejecutar(RAIZ)` produce los tres archivos de `data/processed` idénticos byte a byte (`4ad2487500af`, `48da91b36f78`, `b8d2bf14c28f`) y `assert_frame_equal` lo confirma. `data/processed` no se reescribe.
- **Eficiencia (la medición cambió dos decisiones):**
  - fusión de intervalos: la iterativa reemplaza a la recursiva en el pipeline. Con los datos de octubre las dos tardan menos de 1 ms y la proporción varía entre ejecuciones (1,2 a 2 veces), así que decide el crecimiento: con 900 intervalos en un sitio, más de 2.000 veces, con 6,3 MB contra 0,01 MB, y la recursiva falla con `RecursionError` sobre unos 1.000 intervalos. La recursiva se conserva en `utilidades.py` como referencia y en las pruebas;
  - marcadores de vacío: la versión vectorizada con `isin` es unas 2 veces más rápida (2,0 a 2,4 según la ejecución) que llamar a `es_vacio` en cada una de las 1.055.558 celdas, con la misma memoria;
  - separar sitios: se conserva la de F2, porque la vectorizada no alcanzó la regla (entre 0,9 y 1,3 veces).
  - Regla fijada antes de medir: se cambia solo si la alternativa es al menos 1,5 veces más rápida.
- **Error encontrado al probar la división entrenamiento/prueba:** `UnificadorVariantes` dejaba vacía una categoría que no había visto al ajustar (por ejemplo, `q_sitios` = 21), y la conversión de tipos fallaba. Con el conjunto completo no se notaba. Se corrigió para conservar el valor y se agregó la prueba del caso.
- **Pruebas:** 30 en `tests/test_nucleo.py` (11 normales, 10 límite y 9 de excepción), con `unittest`. Comando: `.venv\Scripts\python.exe -m unittest discover -s tests -v`.
- **Notebook F3** (`F3/F3_Nucleo_Eficiencia_POO.ipynb`): arquitectura generada desde el código, clases y principios, pipeline y patrones, división sin fuga de datos, equivalencia, mediciones con su gráfico (`docs/figuras/f3_fusion_crecimiento.png`), pruebas, `docs/metadatos_fase3.json` y el contrato con la Fase 4 (`data/processed/diccionario_f3.csv` y `parametros_f3.csv`, armados con un segundo observador del pipeline).
- **Limitación declarada:** 5.320 incidencias sin duración válida (5.318 abiertas al exportar y 2 negativas). La mediana imputada se usa solo en el conjunto para modelos; la tabla de recurrencia usa las fechas reales y deja las abiertas aparte.
- **Enfoque descartado:**
  - **una clase `Preprocesador` que hiciera todo:** juntaba 15 pasos en una sola clase, con baja cohesión, y no permitía medir ni probar cada paso por separado;
  - **convertir todas las funciones en clases:** la mayoría no aprende nada; serían clases sin estado, que la guía desaconseja.

## Paso 27 · Códigos de servicio y tramos codificados (17-11-2026)

- **Qué se encontró:** la auditoría independiente del informe revisó `data/raw` columna por columna y encontró dos columnas que el anonimizador no tocaba:
  - `Código de Servicio`: 1.057 valores con números, que corresponden a números de cliente de la distribuidora eléctrica de cada sitio;
  - `Tramo Afectado`: un valor con el nombre de un equipo y de un circuito del proveedor.
- **Qué se hizo:** el anonimizador codifica las dos columnas con la misma regla de los códigos TX (`SRV_0001`… y `TRA_001`), solo en los valores que tienen algún número; "Pendiente", "MW WOM" o "n/a" se conservan. En `data/raw` cambian solo esas dos columnas: se comprobó que las otras 47 quedan idénticas y que los vacíos no cambian.
- **Historial:** el `data/raw` antiguo se reemplazó por el codificado en todos los commits y el repositorio se volvió a crear, porque los pull request guardaban los commits antiguos. Los pull request #1 a #3 se rehicieron con las mismas ramas y los mismos commits; la búsqueda en las 296 versiones de archivos del historial no encuentra ninguno de los valores originales.
- **Efecto en los resultados:** ninguno. El pipeline elimina las dos columnas (una está fuera de alcance y la otra supera el 95 % de vacíos), así que los tres archivos de `data/processed` siguen idénticos a los de la Fase 2 y las 30 pruebas pasan. F1, F2 y F3 se ejecutaron de nuevo para registrar la huella nueva de `data/raw`.
- **Enfoque descartado:** borrar las dos columnas de `data/raw`. Cambiaba la forma del archivo (49 columnas) que verifican F1, F2 y F3, y la Fase 1 mide justamente cuántos vacíos tiene cada columna.

---

## Historial de commits y criterio que respalda cada uno

| Commit | Mensaje | Qué guarda | Producto del enunciado | Criterio de la rúbrica |
|---|---|---|---|---|
| `c7469f7` | docs: crea estructura inicial del proyecto | Carpetas F1 a F4, data, docs, src y scripts; `.gitignore`; README inicial | 2. Repositorio con carpetas F1 y F2 | 8 Repositorio GitHub · 6 Control de versiones |
| `d7c9945` | data: incorpora incidencias de octubre 2026 anonimizadas en raw | El conjunto de datos de entrada, ya anonimizado | 4. Obtención de datos (F2) | 10 Preprocesamiento (punto de partida) · 5 Reproducibilidad (los datos están en el repo) |
| `22d3bd5` | docs: agrega bitácora del proceso y script de anonimización | Esta bitácora y el programa que preparó los datos | 5. Evidencias de trazabilidad | 7 Documentación del proceso · 11 Validación (verificación de la anonimización) |
| `ed3bcfd` | feat: define el entorno reproducible con requirements.txt | Las 105 dependencias con versión fija | 2. Archivo de dependencias | 5 Reproducibilidad técnica · 4 Herramientas científicas |
| `61aea75` | docs: registra el entorno reproducible y la relación de cada commit con la rúbrica | Pasos 11 a 13 de esta bitácora y esta tabla | 5. Evidencias de trazabilidad | 7 Documentación del proceso · 6 Control de versiones |
| `70a2144` | feat: agrega módulo utilidades con funciones, clase y excepción propia | `src/utilidades.py` | 3. Notebook F1 (código modular) | 9 Codificación · 12 Notebook F1 |
| `d33287c` | data: valida el conjunto con validar_dataset.py del curso | `validar_dataset.py` y `docs/validacion_dataset.md` | 4. Obtención de datos | 11 Validación · 3 Problemática (requisitos del dataset) |
| `7ab07a0` | feat: notebook F1 con definición, entorno, ficha, diccionario y validación | Notebook F1, README generado y productos de `docs/` | 3. Notebook F1 | 12 Notebook F1 · 3 Problemática · 5 Reproducibilidad · 14 Vinculación con el mapa |
| `97b3766` | docs: ajusta la problemática al foco en fallas de transmisión | Pregunta, objetivos y alcance nuevos; sección 5.5; README y bitácora | 1. Informe (problemática) · 3. Notebook F1 | 3 Problemática · 7 Documentación del proceso |
| `a01920f` | docs: define el uptime por criticidad y guarda la ejecución de F1 | Criticidades que afectan el uptime y duraciones inválidas (el notebook quedó sin salidas) | 3. Notebook F1 · 5. Evidencias | 3 Problemática · 11 Validación |
| `131cab6` | fix: guarda las salidas de la ejecución del notebook F1 | Notebook F1 ejecutado: numeración 1 a 22, 0 errores, 8 de 8 | 3. Notebook F1 | 12 Notebook F1 · 5 Reproducibilidad |
| `4bbb358` | feat: agrega funciones del pipeline F2 a utilidades y repara la Ñ | `src/utilidades.py`: `huella_sha256`, `es_vacio`, `clasificar_enlace`, `fusionar_intervalos` (recursiva) y la corrección de `reparar_texto` | 4. Notebooks F2 (código) | 9 Codificación · RA2 recursión |
| `bb16016` | feat: notebook F2 con limpieza, transformación, escalamiento y validación | Notebook F2 ejecutado, figuras, metadatos y diccionario del modelo | 4. Notebooks F2 · 5. Evidencias | 13 Notebook F2 · 10 Preprocesamiento · 11 Validación |
| `63a1bae` | data: guarda los conjuntos procesados y la tabla de recurrencia | `data/processed/` (3 archivos) | 4. Notebooks F2 (salida) | 10 Preprocesamiento · 5 Reproducibilidad |
| `4bd3f1b` | docs: registra las decisiones y el proceso de la Fase 2 | `docs/bitacora_decisiones.md` y este paso 18 | 5. Evidencias de trazabilidad | 7 Documentación del proceso |
| `2c91181` | data: conserva los mnemónicos reales de los sitios en data/raw | Anonimizador ajustado, `data/raw` regenerado y validación del dataset | 4. Obtención de datos | 10 Preprocesamiento · 3 Problemática |
| `2ca9b4f` | feat: agrega separar_sitios para contar las fallas por sitio | `src/utilidades.py` | 4. Notebooks F2 (código) | 9 Codificación |
| `862650d` | docs: F1 con mnemónicos reales, definición de criticidad y conteo por sitio | README y productos de `docs/` (el notebook quedó sin salidas; lo corrige `504af47`) | 3. Notebook F1 | 12 Notebook F1 · 3 Problemática |
| `954d6f4` | feat: F2 cuenta la recurrencia por sitio con las reglas del NOC | Figuras y metadatos (el notebook quedó sin salidas; lo corrige `504af47`) | 4. Notebooks F2 | 13 Notebook F2 · 10 Preprocesamiento · 11 Validación |
| `fc557b8` | data: regenera los conjuntos procesados con la tabla por sitio | `data/processed/` | 4. Notebooks F2 (salida) | 10 Preprocesamiento |
| `44c4803` | docs: registra el cambio a mnemónicos reales y el conteo por sitio | Paso 19 de esta bitácora y bitácora de decisiones | 5. Evidencias | 7 Documentación del proceso |
| `504af47` | fix: guarda las salidas de F1 y F2 ejecutados con los mnemónicos reales | Notebooks ejecutados y guardados, `data/processed` y `docs/` de esa ejecución | 3 y 4. Notebooks F1 y F2 | 12 y 13 Notebooks · 5 Reproducibilidad |
| `6cfd05b` | docs: agrega el mapa conceptual del flujo reproducible | `scripts/mapa_conceptual.py`, la figura y los pasos 19 y 20 de esta bitácora | 1. Informe (apartado VIII) | 14 Vinculación con el mapa · 7 Documentación |
| (pull request) | Merge de f2-pipeline en main | Integración de la Fase 2 | 2. Repositorio | 6 Control de versiones (ramas) · 8 Repositorio |
| `c5fc311` | docs: registra la prueba desde cero del repositorio | Paso 21 de esta bitácora | 5. Evidencias de trazabilidad | 5 Reproducibilidad · 7 Documentación |
| `25750d7` | docs: reescribe las restricciones del proyecto en F1 | Notebook F1 ejecutado, README y productos de `docs/` | 3. Notebook F1 · 1. Informe | 3 Problemática · 12 Notebook F1 |
| `69aca6d` | feat: F2 cuenta solo los minutos de octubre para el uptime | Notebook F2 ejecutado, figuras, metadatos y bitácora de decisiones | 4. Notebooks F2 | 13 Notebook F2 · 10 Preprocesamiento |
| `a5f8c5f` | data: regenera la tabla de recurrencia con el corte al 31-10 | `data/processed/` | 4. Notebooks F2 (salida) | 10 Preprocesamiento |
| `663037e` | docs: registra las restricciones nuevas y el corte al 31-10 | Paso 22 de esta bitácora | 5. Evidencias | 7 Documentación del proceso |
| `beb5b5e` | fix: corrige textos de F1, F2 y el mapa según la auditoría | Notebooks F1 y F2 ejecutados, README, `docs/` y mapa | 3 y 4. Notebooks · 1. Informe | 12 y 13 Notebooks · 14 Vinculación · 7 Documentación |
| `6f7b49e` | docs: registra las correcciones de la auditoría | Paso 23 de esta bitácora | 5. Evidencias | 7 Documentación del proceso |
| `0676823` | fix: deja en requirements.txt solo las librerías del proyecto | 6 librerías con versión fija | 2. Archivo de dependencias | 5 Reproducibilidad |
| `52efc82` | feat: prueba la instalación en Linux, macOS y Windows con GitHub Actions | `.github/workflows/instalacion.yml` | 2. Repositorio · 5. Evidencias | 5 Reproducibilidad · 6 Control de versiones |
| `e36b384` | docs: registra el repositorio privado y las dependencias del proyecto | Paso 24 de esta bitácora | 5. Evidencias | 7 Documentación del proceso |
| `00a152e` | Merge pull request #1 from edgararciav-cpu/f3-dependencias | Integración del componente de dependencias | 2. Repositorio | 6 Control de versiones (ramas) |
| `1e004ac` | fix: codifica los sitios y omite el texto libre en el anonimizador | `scripts/anonimizar_incidencias.py` y `data/raw` con códigos | S2 · IV Repositorio | Confidencialidad pedida en la retroalimentación |
| `80ea4a1` | docs: describe los sitios como códigos en el módulo y en el mapa | `src/utilidades.py` y mapa conceptual | S2 · III.b Documentación | Confidencialidad |
| `5bda65b` | feat: F1 y F2 ejecutados con los sitios codificados | Notebooks, `data/processed` y `docs/` | S2 · V Notebooks | Reproducibilidad |
| `d639676` | docs: registra la confidencialidad de los datos y los hashes nuevos | Paso 25 y `docs/equivalencia_commits_reescritura.csv` | S2 · IV Repositorio | Trazabilidad |
| `ab6c2eb` | Merge pull request #2 from edgararciav-cpu/f3-confidencialidad | Integración del componente de confidencialidad | S2 · IV Repositorio | Ramas por componente |
| `b5ce606` | feat: traslada a src las funciones de F2 que no aprenden de los datos | `src/__init__.py`, `carga.py`, `limpieza.py` | S2 · II.a Codificación | II.e Diseño estructurado |
| `fcad3ed` | feat: clase base Transformador y clases que aprenden de los datos | `src/transformadores.py` | S2 · III.a POO | II.b Preprocesamiento |
| `d7ef4a8` | feat: pipeline que ejecuta la Fase 2 en una llamada, con bitácora observadora | `src/pipeline.py` | S2 · III.a POO · III.b Patrones | II.b Preprocesamiento |
| `18d2d85` | feat: medición de tiempo y memoria y fusión de intervalos iterativa | `src/medicion.py`, `src/utilidades.py` | S2 · II.d Eficiencia | II.e Recursividad |
| `2f45c60` | test: pruebas normales, límite y de excepción, y equivalencia con la Fase 2 | `tests/test_nucleo.py` | S2 · II.c Validación | V Notebooks |
| `daed972` | perf: vacíos vectorizados y fusión iterativa por defecto, según la medición | `src/limpieza.py`, `src/utilidades.py`, pruebas | S2 · II.d Eficiencia | La medición cambia la decisión |
| `f9539aa` | fix: UnificadorVariantes conserva los valores que no vio al ajustar | `src/transformadores.py` y su prueba | S2 · II.c Validación | III.a POO (ajustar/transformar) |
| `858583a` | docs: cifras de eficiencia como rangos, porque varían entre ejecuciones | `src/limpieza.py` y paso 26 | S2 · II.d Eficiencia | Medición honesta |
| `9e7df9d` | feat: notebook F3 ejecutado con clases, equivalencia, eficiencia, pruebas y contrato con la Fase 4 | Notebook F3, `diccionario_f3.csv`, `parametros_f3.csv`, mediciones y metadatos | S2 · V Notebooks | III.b Documentación |
| `02dd194` | docs: actualiza los hashes de commits citados en la bitácora, los metadatos y los notebooks | Referencias a commits | S2 · IV Repositorio | Trazabilidad |
| `0ac03fa` | Merge pull request #3 from edgararciav-cpu/f3-nucleo | Integración del núcleo de la Fase 3 | S2 · IV Repositorio | Ramas por componente |
| `7bef7bf` | docs: registra en la bitácora los merges de los pull request de la Fase 3 | Tabla de commits | S2 · IV Repositorio | Trazabilidad |
| `dd5a032` | docs: agrega .mailmap para que Git muestre una sola identidad del autor | `.mailmap` | S2 · IV Repositorio | Contribuciones identificables |
| `213015b` | docs: objetivos analíticos, metodología y vinculación con el mapa al cierre de la Fase 3 | F1 ejecutado, README y `docs/` | S2 · II (objetivos) | Corrección 2 de la S1 |
| `7a7e26f` | fix: unifica variantes sin el aviso de pandas y precisa textos de carga, limpieza y bitácora | `src/` y bitácora | S2 · II.c Validación | Correcciones de la auditoría |
| `0c97d30` | fix: el anonimizador también codifica Código de Servicio y Tramo Afectado | `scripts/anonimizar_incidencias.py` | S2 · IV Repositorio | Confidencialidad (paso 27) |

Convención de prefijos:

| Prefijo | Uso |
|---|---|
| `docs:` | documentación |
| `data:` | datos |
| `feat:` | algo nuevo que hace funcionar el proyecto |
| `fix:` | corrección |
| `test:` | pruebas |
| `perf:` | cambio de implementación justificado por una medición |
