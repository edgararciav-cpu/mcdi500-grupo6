"""
Anonimiza el export de incidencias del NOC antes de usarlo en el proyecto MCDI500.

Qué hace
- Reemplaza por códigos los nombres de personas y los identificadores comerciales:
    Incident Manager       -> IM_01, IM_02, ...
    Creador de TT          -> OP_01, OP_02, ...
    Ticket de proveedor    -> TKP_0001, ...
    Código servicio TX 1-5 -> TXS_0001, ...
    Código de Servicio     -> SRV_0001, ...   (números de cliente de la distribuidora eléctrica)
    Tramo Afectado         -> TRA_001, ...    (nombres de equipos y circuitos del proveedor)
- Reemplaza cada sitio de Network Element por un código, SIT_0001, SIT_0002, ..., en el orden en
  que aparece. Si una celda trae varios sitios (separados por dos o más espacios), cada uno recibe
  su código y se conservan los separadores, así que la cantidad de sitios por celda no cambia.
- El texto libre (Titulo y Detalle) se reemplaza por "[texto omitido]": nombra sitios, equipos y
  tickets internos, y el análisis no lo usa. Las celdas vacías y los marcadores de vacío (NA, N/A,
  no aplica...) se dejan como están, para que la medición de vacíos de la Fase 1 no cambie.
- No toca nada más: deja los errores de tildes, las categorías mal escritas y los vacíos,
  porque limpiarlos es el trabajo de la Fase 2.
- Por qué los sitios van con código (decisión del 15-11-2026): son información operativa interna
  del operador. La versión del 11-11 los dejaba con su nemónico real y el docente pidió
  reemplazarlos y limpiar el historial del repositorio.
- No guarda en el proyecto la tabla de equivalencias (nombre -> código). Si se pasa una tercera ruta,
  escribe ahí la equivalencia de los sitios, para uso interno del NOC: esa ruta debe quedar FUERA del
  repositorio.

Uso (desde esta carpeta):
    python anonimizar_incidencias.py ORIGEN.csv DESTINO.csv [EQUIVALENCIAS_SITIOS.csv]
"""
import csv
import re
import sys

# Columna (nombre ya corregido) -> prefijo del código y cantidad de dígitos
A_CODIFICAR = {
    'Incident Manager': ('IM', 2),
    'Creador de TT': ('OP', 2),
    'Ticket de proveedor': ('TKP', 4),
    'Código servicio TX 1': ('TXS', 4),
    'Código servicio TX 2': ('TXS', 4),
    'Código servicio TX 3': ('TXS', 4),
    'Código servicio TX 4': ('TXS', 4),
    'Código servicio TX 5': ('TXS', 4),
    'Código de Servicio': ('SRV', 4),
    'Tramo Afectado': ('TRA', 3),
}
# En tickets, códigos de servicio y tramos solo se codifican los valores con algún número: "Pendiente",
# "ENEL" o "MW WOM" no son identificadores sino marcadores, y se dejan tal cual para tratarlos en la Fase 2.
SOLO_CON_NUMERO = {'TKP', 'TXS', 'SRV', 'TRA'}

COLUMNA_SITIOS = 'Network Element'
PREFIJO_SITIO, DIGITOS_SITIO = 'SIT', 4
SEPARADOR_SITIOS = re.compile(r'(\s{2,})')   # dos o más espacios separan sitios; uno solo es parte del nombre

COLUMNAS_TEXTO = ['Titulo', 'Detalle']
TEXTO_OMITIDO = '[texto omitido]'
MARCADORES_VACIO = {'', 'na', 'n/a', 'no aplica', '-', '0000-00-00 00:00:00'}


def debe_codificar(prefijo, valor):
    return bool(valor) and (prefijo not in SOLO_CON_NUMERO or any(ch.isdigit() for ch in valor))


def nombre_limpio(columna):
    """Nombre de columna legible: quita el </div>, los BOM y repara las tildes rotas (Ã³ -> ó)."""
    c = columna.replace('﻿', '').replace('</div>', '').replace('ï»¿', '').strip()
    try:
        return c.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return c


def codificar_sitios(celda, codigos):
    """Reemplaza cada sitio de la celda por su código (lo crea si es nuevo) y conserva los separadores."""
    partes = SEPARADOR_SITIOS.split(celda)
    for k in range(0, len(partes), 2):           # posiciones pares: sitios; impares: separadores
        sitio = partes[k].strip()
        if not sitio:
            continue
        if sitio not in codigos:
            codigos[sitio] = f'{PREFIJO_SITIO}_{len(codigos) + 1:0{DIGITOS_SITIO}d}'
        partes[k] = partes[k].replace(sitio, codigos[sitio])
    return ''.join(partes)


def main(origen, destino, equivalencias=None):
    with open(origen, encoding='utf-8', newline='') as f:
        filas = list(csv.reader(f, delimiter=';'))
    cabecera, datos = filas[0], filas[1:]
    limpios = [nombre_limpio(c) for c in cabecera]

    faltan = [c for c in [*A_CODIFICAR, COLUMNA_SITIOS, *COLUMNAS_TEXTO] if c not in limpios]
    if faltan:
        sys.exit(f'No encontré estas columnas en el archivo: {faltan}')

    # 1) Asignar códigos en orden de aparición (cada prefijo lleva su propia numeración)
    codigos, contador = {}, {}
    for col, (prefijo, digitos) in A_CODIFICAR.items():
        i = limpios.index(col)
        for fila in datos:
            v = fila[i].strip()
            if debe_codificar(prefijo, v) and (prefijo, v) not in codigos:
                contador[prefijo] = contador.get(prefijo, 0) + 1
                codigos[(prefijo, v)] = f'{prefijo}_{contador[prefijo]:0{digitos}d}'

    # 2) Reemplazar en sus columnas
    for col, (prefijo, _) in A_CODIFICAR.items():
        i = limpios.index(col)
        for fila in datos:
            v = fila[i].strip()
            if debe_codificar(prefijo, v):
                fila[i] = codigos[(prefijo, v)]

    # 3) Sitios: un código por sitio, también en las celdas con varios sitios
    i_sitios = limpios.index(COLUMNA_SITIOS)
    sitios = {}
    for fila in datos:
        fila[i_sitios] = codificar_sitios(fila[i_sitios], sitios)

    # 4) Texto libre: se omite (los marcadores de vacío se conservan)
    omitidas = 0
    for col in COLUMNAS_TEXTO:
        i = limpios.index(col)
        for fila in datos:
            if fila[i].strip().lower() not in MARCADORES_VACIO:
                fila[i], omitidas = TEXTO_OMITIDO, omitidas + 1

    # 5) Verificar que ningún sitio real ni nombre de persona quede en todo el archivo
    reales = [v for (p, v) in codigos if p in {'IM', 'OP'}] + list(sitios)
    patron = re.compile(r'(?<![\w-])(' + '|'.join(re.escape(v) for v in sorted(reales, key=len, reverse=True)) + r')(?![\w-])')
    quedan = sum(1 for fila in datos for v in fila if patron.search(v))

    with open(destino, 'w', encoding='utf-8', newline='') as f:
        csv.writer(f, delimiter=';', lineterminator='\r\n').writerows([cabecera] + datos)
    if equivalencias:
        with open(equivalencias, 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f, delimiter=';')
            w.writerow(['codigo', 'sitio'])
            w.writerows((c, s) for s, c in sitios.items())

    print(f'Filas leídas y escritas: {len(datos)} | columnas: {len(cabecera)}')
    for prefijo in sorted(contador):
        print(f'  {prefijo}: {contador[prefijo]} valores distintos reemplazados por código')
    print(f'  {PREFIJO_SITIO}: {len(sitios)} sitios distintos reemplazados por código')
    print(f'Celdas de texto libre omitidas: {omitidas}')
    print('Verificación: ' + ('OK, no queda ningún valor original.' if quedan == 0 else f'ATENCIÓN, quedan {quedan} celdas con valores originales.'))
    print(f'Archivo anonimizado: {destino}')
    if equivalencias:
        print(f'Equivalencias de sitios (uso interno, fuera del repositorio): {equivalencias}')


if __name__ == '__main__':
    if len(sys.argv) not in (3, 4):
        sys.exit('Uso: python anonimizar_incidencias.py ORIGEN.csv DESTINO.csv [EQUIVALENCIAS_SITIOS.csv]')
    main(*sys.argv[1:])
