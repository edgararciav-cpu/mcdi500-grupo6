"""Utilidades del proyecto MCDI500 · Incidencias de red (Grupo 6).

Funciones reutilizables que usan los notebooks de todas las fases. Se importan con:

    import utilidades

después de agregar la carpeta src/ a sys.path (lo hace la primera celda de cada notebook).
"""

import hashlib
import re
import unicodedata
from pathlib import Path

import pandas as pd

# Formas en que el exporte escribe "no hay dato". Se comparan sin mayúsculas ni espacios extremos.
MARCADORES_VACIO = {"", "na", "n/a", "no aplica", "-", "0000-00-00 00:00:00"}

# Criticidades con pérdida de servicio: son las que bajan el uptime (definición operativa del NOC).
CRITICIDAD_UPTIME = ("P1", "P2", "P3", "P3E")


class ProyectoError(Exception):
    """Error propio del proyecto: distingue "los datos vienen mal" de un fallo de pandas."""


def reparar_texto(texto):
    """Repara tildes rotas por doble codificación ("EnergÃ­a" -> "Energía").

    Si el texto no tiene ese problema, lo devuelve igual. No modifica valores que no son texto.
    """
    if not isinstance(texto, str):
        return texto
    limpio = texto.replace("﻿", "").replace("</div>", "").replace("ï»¿", "")
    if "Ã" not in limpio and "Â" not in limpio:
        return limpio
    # cp1252 primero: la Ñ rota ("Ã‘") usa un carácter (‘) que existe en cp1252 y no en latin-1
    for codificacion in ("cp1252", "latin-1"):
        try:
            return limpio.encode(codificacion).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    return limpio


def normalizar_nombre(texto):
    """Convierte un nombre de columna a snake_case sin tildes: "Tipo Incidencia NOC" -> "tipo_incidencia_noc"."""
    if not isinstance(texto, str) or not texto.strip():
        raise ProyectoError(f"nombre de columna inválido: {texto!r}")
    texto = reparar_texto(texto)
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", sin_tildes.lower()).strip("_")


def normalizar_columnas(nombres):
    """Aplica normalizar_nombre a una lista de nombres y verifica que no queden repetidos."""
    nuevos = [normalizar_nombre(n) for n in nombres]
    repetidos = sorted({n for n in nuevos if nuevos.count(n) > 1})
    if repetidos:
        raise ProyectoError(f"nombres repetidos después de normalizar: {repetidos}")
    return nuevos


def duracion_a_minutos(texto):
    """Convierte una duración "h:mm:ss" (las horas pueden pasar de 24) a minutos.

    Devuelve NaN si el valor está vacío. Lanza ProyectoError si el formato no es válido.
    """
    if texto is None or (isinstance(texto, float) and pd.isna(texto)) or str(texto).strip() == "":
        return float("nan")
    partes = str(texto).strip().split(":")
    if len(partes) != 3 or not all(p.isdigit() for p in partes):
        raise ProyectoError(f"duración con formato inválido: {texto!r}")
    horas, minutos, segundos = (int(p) for p in partes)
    if minutos >= 60 or segundos >= 60:
        raise ProyectoError(f"minutos o segundos fuera de rango: {texto!r}")
    return horas * 60 + minutos + segundos / 60


def huella_sha256(ruta):
    """Huella SHA-256 de un archivo: si cambia un solo byte, cambia la huella."""
    return hashlib.sha256(Path(ruta).read_bytes()).hexdigest()


def es_vacio(valor):
    """True si el valor es un marcador de "sin dato" (NA, N/A, no aplica, vacío...)."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return True
    return str(valor).strip().lower() in MARCADORES_VACIO


def separar_sitios(texto):
    """Lista de sitios (códigos) de una celda de Network Element.

    Cuando una incidencia afecta varios sitios, el exporte los escribe en la misma celda separados
    por DOS o más espacios ("SIT_0002  SIT_0003"). Un espacio simple es parte del nombre
    ("SITIO NORTE"). Lanza ProyectoError si la celda está vacía.
    """
    if not isinstance(texto, str) or not texto.strip():
        raise ProyectoError(f"celda de sitios vacía: {texto!r}")
    return re.split(r"\s{2,}", texto.strip())


def clasificar_enlace(tipo_incidencia, incidencia):
    """Tipo de enlace de transmisión que falló, a partir del tipo y la incidencia NOC.

    Devuelve "Microondas", "Fibra propia (FOP)", "Fibra proveedor", "Satelital" u "Otra TX".
    Si la incidencia no es de transmisión devuelve None. Lanza ProyectoError si falta el texto.
    """
    if tipo_incidencia not in ("Tx Propia", "Tx Proveedor"):
        return None
    if not isinstance(incidencia, str) or not incidencia.strip():
        raise ProyectoError(f"falla de transmisión sin incidencia NOC: {incidencia!r}")
    texto = incidencia.strip().lower()
    if texto.startswith("mw"):
        return "Microondas"
    if texto.startswith("fop"):
        return "Fibra propia (FOP)"
    if "satelital" in texto:
        return "Satelital"
    if tipo_incidencia == "Tx Proveedor":
        return "Fibra proveedor"
    return "Otra TX"


def fusionar_intervalos(intervalos):
    """Une intervalos (inicio, fin) que se traslapan. Función RECURSIVA.

    Si un elemento de red tiene dos incidencias abiertas al mismo tiempo, sumar sus duraciones
    contaría dos veces el mismo tiempo fuera de servicio. Esta función devuelve los intervalos sin
    traslape, ordenados.

    Caso base: 0 o 1 intervalo, no hay nada que unir.
    Paso recursivo: se fusionan los intervalos desde el segundo en adelante, y luego se decide si
    el primero se une con el primero de ese resultado o queda aparte.
    """
    ordenados = sorted(intervalos)
    for inicio, fin in ordenados:
        if fin < inicio:
            raise ProyectoError(f"intervalo con fin anterior al inicio: {(inicio, fin)}")
    if len(ordenados) <= 1:
        return ordenados
    primero, resto = ordenados[0], fusionar_intervalos(ordenados[1:])
    siguiente = resto[0]
    if siguiente[0] <= primero[1]:                       # se traslapan o se tocan: un solo intervalo
        unido = (primero[0], max(primero[1], siguiente[1]))
        # el intervalo unido puede alcanzar a los que siguen: se vuelve a fusionar (la lista es 1 más corta)
        return fusionar_intervalos([unido] + resto[1:])
    return [primero] + resto


class ConjuntoDatos:
    """Describe un archivo de datos del proyecto y lo carga siempre de la misma forma.

    Reúne en un objeto la ruta, el separador y la codificación, para que todas las fases
    lean el archivo igual (reproducibilidad).
    """

    def __init__(self, ruta, sep=";", encoding="utf-8-sig"):
        self.ruta = Path(ruta)
        self.sep = sep
        self.encoding = encoding

    def existe(self):
        return self.ruta.is_file()

    def cargar(self, como_texto=False):
        """Lee el archivo. Con como_texto=True no convierte tipos ni vacíos (útil para auditar)."""
        if not self.existe():
            raise ProyectoError(f"no existe el archivo {self.ruta}")
        opciones = {"sep": self.sep, "encoding": self.encoding, "low_memory": False}
        if como_texto:
            opciones.update(dtype=str, keep_default_na=False)
        return pd.read_csv(self.ruta, **opciones)

    def resumen(self, df=None):
        """Tabla con tipo, valores únicos y % de vacíos por columna."""
        df = self.cargar() if df is None else df
        return pd.DataFrame({
            "dtype": df.dtypes.astype(str),
            "n_unicos": df.nunique(),
            "pct_nulos": (df.isna().mean() * 100).round(2),
        })

    def __repr__(self):
        return f"ConjuntoDatos({self.ruta.name!r}, sep={self.sep!r}, encoding={self.encoding!r})"
