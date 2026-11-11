"""
Anonimiza el export de incidencias del NOC antes de usarlo en el proyecto MCDI500.

Qué hace
- Reemplaza por códigos los nombres de personas y los identificadores de red:
    Incident Manager       -> IM_01, IM_02, ...
    Creador de TT          -> OP_01, OP_02, ...
    Network Element        -> NE_0001, ...
    Ticket de proveedor    -> TKP_0001, ...
    Código servicio TX 1-5 -> TXS_0001, ...
- Si alguno de esos valores aparece escrito dentro de otra columna (por ejemplo en Titulo o Detalle),
  también lo reemplaza por su código.
- No toca nada más: deja los errores de tildes, las categorías mal escritas y los vacíos,
  porque limpiarlos es el trabajo de la Fase 2.
- No guarda la tabla de equivalencias (nombre -> código), así que el resultado no se puede revertir.

Uso (desde esta carpeta):
    python anonimizar_incidencias.py ORIGEN.csv DESTINO.csv
"""
import csv
import re
import sys

# Columna (nombre ya corregido) -> prefijo del código y cantidad de dígitos
A_CODIFICAR = {
    'Incident Manager': ('IM', 2),
    'Creador de TT': ('OP', 2),
    'Network Element': ('NE', 4),
    'Ticket de proveedor': ('TKP', 4),
    'Código servicio TX 1': ('TXS', 4),
    'Código servicio TX 2': ('TXS', 4),
    'Código servicio TX 3': ('TXS', 4),
    'Código servicio TX 4': ('TXS', 4),
    'Código servicio TX 5': ('TXS', 4),
}
LARGO_MINIMO_EN_TEXTO = 4  # valores más cortos no se buscan dentro del texto, para no reemplazar por error
# Solo se buscan dentro de texto libre los nombres de personas y de elementos de red,
# y solo en estas columnas. Los tickets y códigos TX no, porque algunos son palabras comunes.
PREFIJOS_EN_TEXTO = {'IM', 'OP', 'NE'}
COLUMNAS_TEXTO = ['Titulo', 'Detalle']
# En tickets y códigos TX solo se codifican los valores con algún número: "Pendiente" o "ENEL"
# no son códigos sino marcadores, y se dejan tal cual para tratarlos en la Fase 2.
SOLO_CON_NUMERO = {'TKP', 'TXS'}


def debe_codificar(prefijo, valor):
    return bool(valor) and (prefijo not in SOLO_CON_NUMERO or any(ch.isdigit() for ch in valor))


def nombre_limpio(columna):
    """Nombre de columna legible: quita el </div>, los BOM y repara las tildes rotas (Ã³ -> ó)."""
    c = columna.replace('﻿', '').replace('</div>', '').replace('ï»¿', '').strip()
    try:
        return c.encode('latin-1').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return c


def main(origen, destino):
    with open(origen, encoding='utf-8', newline='') as f:
        filas = list(csv.reader(f, delimiter=';'))
    cabecera, datos = filas[0], filas[1:]
    limpios = [nombre_limpio(c) for c in cabecera]

    faltan = [c for c in A_CODIFICAR if c not in limpios]
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

    # 3) Reemplazar nombres de personas y de elementos de red escritos dentro del texto libre
    por_valor = {v: c for (p, v), c in codigos.items() if p in PREFIJOS_EN_TEXTO and len(v) >= LARGO_MINIMO_EN_TEXTO}
    patron = re.compile(r'(?<![\w-])(' + '|'.join(re.escape(v) for v in sorted(por_valor, key=len, reverse=True)) + r')(?![\w-])')
    columnas_texto = [limpios.index(c) for c in COLUMNAS_TEXTO if c in limpios]
    en_texto = 0
    for fila in datos:
        for i in columnas_texto:
            nuevo, n = patron.subn(lambda m: por_valor[m.group(1)], fila[i])
            if n:
                fila[i], en_texto = nuevo, en_texto + n

    # 4) Verificar que ningún nombre de persona ni elemento de red quede en todo el archivo
    quedan = sum(1 for fila in datos for v in fila if patron.search(v))
    with open(destino, 'w', encoding='utf-8', newline='') as f:
        csv.writer(f, delimiter=';', lineterminator='\r\n').writerows([cabecera] + datos)

    print(f'Filas leídas y escritas: {len(datos)} | columnas: {len(cabecera)}')
    for prefijo in sorted(contador):
        print(f'  {prefijo}: {contador[prefijo]} valores distintos reemplazados por código')
    print(f'Reemplazos dentro de texto libre: {en_texto}')
    print('Verificación: ' + ('OK, no queda ningún valor original.' if quedan == 0 else f'ATENCIÓN, quedan {quedan} celdas con valores originales.'))
    print(f'Archivo anonimizado: {destino}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Uso: python anonimizar_incidencias.py ORIGEN.csv DESTINO.csv')
    main(sys.argv[1], sys.argv[2])
