"""Carga del conjunto de datos de entrada (data/raw).

Una sola responsabilidad: leer el archivo siempre de la misma forma y comprobar que tiene la forma (filas y
columnas) que registró la Fase 1. Devuelve también su huella SHA-256, para que quien lo use la compare con la de
otra fase. Si algo no calza, se detiene antes de procesar nada.
"""
import json
from pathlib import Path

from . import utilidades


def leer_metadatos_f1(raiz):
    """Metadatos que dejó la Fase 1 (archivo, filas, columnas)."""
    return json.loads((Path(raiz) / "docs" / "metadatos_fase1.json").read_text(encoding="utf-8"))


def cargar_crudo(raiz, verificar=True):
    """Lee data/raw como texto, sin convertir tipos ni vacíos. Devuelve (DataFrame, huella SHA-256).

    Con verificar=True comprueba que la forma sea la que registró la Fase 1; si no, lanza ProyectoError.
    """
    meta = leer_metadatos_f1(raiz)
    conjunto = utilidades.ConjuntoDatos(Path(raiz) / meta["dataset"]["archivo"])
    if not conjunto.existe():
        raise FileNotFoundError(f"No se encontró el archivo de entrada: {conjunto.ruta}")
    crudo = conjunto.cargar(como_texto=True)
    if verificar and crudo.shape != (meta["dataset"]["filas"], meta["dataset"]["columnas"]):
        raise utilidades.ProyectoError(
            f"El archivo tiene forma {crudo.shape} y la Fase 1 registró "
            f"{(meta['dataset']['filas'], meta['dataset']['columnas'])}")
    return crudo, utilidades.huella_sha256(conjunto.ruta)
