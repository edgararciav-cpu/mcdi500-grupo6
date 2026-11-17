"""Operaciones del pipeline que NO aprenden de los datos.

Son funciones, no clases: reciben una tabla y devuelven otra, sin recordar nada entre llamadas
(criterio del docente: una clase se justifica solo si el componente necesita recordar algo).
Es el mismo código de F2_Preprocesamiento.ipynb, trasladado a un módulo para que la Fase 3 lo
importe en vez de copiarlo.
"""
import numpy as np
import pandas as pd

from . import utilidades

# ---------------------------------------------------------------- nombres y texto (F2, secciones 3.1 a 3.3)
CORTOS = {
    "fecha_de_inicio_de_incidencia": "fecha_inicio", "fecha_cierre_de_incidencia": "fecha_cierre",
    "fecha_de_inicio_ticket": "fecha_inicio_ticket", "fecha_de_cierre_de_ticket": "fecha_cierre_ticket",
    "tiempo_de_duracion_de_la_incidencia": "duracion_txt", "tiempo_de_duracion_del_ticket": "duracion_ticket_txt",
    "network_element": "sitios", "q_network_element": "q_sitios", "tiempo_de_respuesta": "tiempo_respuesta_h",
}
TEXTO_LIBRE = ["titulo", "detalle"]


def limpiar_nombres(df, cortos=CORTOS):
    """Repara, normaliza y acorta los nombres de columna. Devuelve una copia."""
    salida = df.copy()
    salida.columns = [cortos.get(n, n) for n in utilidades.normalizar_columnas(list(df.columns))]
    return salida


def reparar_texto(df):
    """Deshace la doble codificación en todas las celdas ("EnergÃ­a" -> "Energía")."""
    return df.apply(lambda col: col.map(utilidades.reparar_texto))


def contar_rotas(df):
    """Celdas que todavía tienen tildes rotas (Ã o Â)."""
    return int(df.apply(lambda col: col.astype(str).str.contains("Ã|Â", regex=True)).sum().sum())


def unificar_vacios_por_celda(df):
    """Versión de la Fase 2: llama a utilidades.es_vacio una vez por celda (más de un millón de llamadas).

    Se conserva para la comparación de eficiencia de la Fase 3 y para las pruebas.
    """
    salida = df.apply(lambda col: col.str.strip())
    marcadores = salida.apply(lambda col: col.map(utilidades.es_vacio))
    return salida.mask(marcadores)


def unificar_vacios(df):
    """Reemplaza todos los marcadores de "sin dato" por NaN y quita espacios extremos.

    Versión vectorizada (Fase 3): compara cada columna completa contra MARCADORES_VACIO con isin, en
    vez de llamar a una función de Python por celda. Mismo resultado que unificar_vacios_por_celda y
    unas 2 veces más rápida sobre los datos reales (medición en F3, sección 6).
    """
    salida = df.apply(lambda col: col.str.strip())
    marcadores = salida.apply(lambda col: col.isna() | col.str.lower().isin(utilidades.MARCADORES_VACIO))
    return salida.mask(marcadores)


# ---------------------------------------------------------------- tipos (F2, sección 3.5)
FORMATO_FECHA = "%d-%m-%Y %H:%M"
COLUMNAS_FECHA = ["fecha_inicio", "fecha_cierre", "fecha_inicio_ticket", "fecha_cierre_ticket"]


def a_minutos_seguro(serie):
    """Convierte h:mm:ss a minutos. Las duraciones con formato inválido quedan NaN. Devuelve (minutos, invalidas)."""
    def convertir(valor):
        try:
            return utilidades.duracion_a_minutos(valor)
        except utilidades.ProyectoError:
            return "invalida"
    resultado = serie.map(convertir)
    invalidas = resultado.eq("invalida")
    return pd.to_numeric(resultado.mask(invalidas), errors="coerce"), invalidas


def a_binaria(serie, si="SI", no="NO"):
    """SI/NO -> 1/0. Lanza ProyectoError si aparece un valor distinto."""
    otros = set(serie.dropna().str.upper()) - {si, no}
    if otros:
        raise utilidades.ProyectoError(f"valores no binarios en {serie.name}: {otros}")
    return serie.str.upper().map({si: 1, no: 0}).astype("Int64")


def convertir_tipos(df):
    """Fechas a datetime, duraciones a minutos (con bandera de inválidas), conteos a entero y SI/NO a 1/0."""
    salida = df.copy()
    for col in COLUMNAS_FECHA:
        salida[col] = pd.to_datetime(salida[col], format=FORMATO_FECHA)
    salida["duracion_min"], invalida = a_minutos_seguro(salida["duracion_txt"])
    salida["duracion_ticket_min"], _ = a_minutos_seguro(salida["duracion_ticket_txt"])
    salida["cierre_invalido"] = invalida.astype(int)
    salida = salida.drop(columns=["duracion_txt", "duracion_ticket_txt"])
    for col in ["q_sitios", "tiempo_respuesta_h"]:
        salida[col] = salida[col].astype(int)
    for col in ["gestionable", "gestor_uptime"]:
        salida[col] = a_binaria(salida[col])
    salida["duracion_faltante"] = salida["duracion_min"].isna().astype(int)
    return salida


# ---------------------------------------------------------------- variables derivadas (F2, sección 4.1)
PROVEEDOR_SATELITAL = "TGS Starlink"     # dato del NOC: el exporte no trae el proveedor de los enlaces satelitales


def derivar_variables(df):
    """Agrega es_tx, tipo_enlace, afecta_uptime, es_extendida, duracion_log, hora, día y región. Devuelve una copia."""
    salida = df.copy()
    salida["es_tx"] = salida["tipo_incidencia_noc"].isin(["Tx Propia", "Tx Proveedor"]).astype(int)
    salida["tipo_enlace"] = [utilidades.clasificar_enlace(t, i)
                             for t, i in zip(salida["tipo_incidencia_noc"], salida["incidencia_noc"])]
    salida["afecta_uptime"] = (salida["criticidad"].isin(utilidades.CRITICIDAD_UPTIME)
                               & salida["estado"].ne("Cancelada")).astype(int)
    salida["es_extendida"] = salida["criticidad"].eq("P3E").astype(int)        # P3 extendida
    sin_proveedor_satelital = salida["tipo_enlace"].eq("Satelital") & salida["proveedor_tx_1"].isna()
    salida.loc[sin_proveedor_satelital, "proveedor_tx_1"] = PROVEEDOR_SATELITAL
    salida["duracion_log"] = np.log1p(salida["duracion_min"])
    salida["hora_inicio"] = salida["fecha_inicio"].dt.hour
    salida["dia_semana"] = salida["fecha_inicio"].dt.day_of_week          # 0 = lunes
    regiones = salida["regiones"].fillna("").str.split(",")
    salida["region_principal"] = regiones.str[0].str.strip().replace("", np.nan)
    salida["n_regiones"] = regiones.map(lambda r: len([x for x in r if x.strip()]))
    return salida


# ---------------------------------------------------------------- ordinales (F2, sección 4.2)
ORDENES = {
    "criticidad": ["P4", "P2 Redundancia", "P2R Degradación", ("P3", "P3E"), "P2", "P1"],
    "impacto": ["Sin Impacto", "Localizado", "Regional", "Amplio"],
}


def codificar_ordinal(serie, orden):
    """Nivel (0 = menor) según el orden declarado. Cada nivel es una categoría o una tupla que comparte nivel.

    No es una clase porque no aprende nada: el orden lo declara el NOC, no los datos.
    Lanza ProyectoError si aparece un valor que no está en el orden.
    """
    nivel = {}
    for i, categorias in enumerate(orden):
        for valor in (categorias if isinstance(categorias, tuple) else (categorias,)):
            nivel[valor] = i
    desconocidos = set(serie.dropna()) - set(nivel)
    if desconocidos:
        raise utilidades.ProyectoError(f"{serie.name}: valores fuera del orden declarado {desconocidos}")
    return serie.map(nivel).astype("Int64")


def codificar_ordinales(df, ordenes=ORDENES):
    """Agrega <variable>_ord para cada variable ordinal. Devuelve una copia."""
    salida = df.copy()
    for variable, orden in ordenes.items():
        salida[f"{variable}_ord"] = codificar_ordinal(salida[variable], orden)
    return salida


def log_duracion_modelo(df):
    """Logaritmo de la duración imputada, que es la que se escala para el conjunto de modelo."""
    salida = df.copy()
    salida["duracion_log_modelo"] = np.log1p(salida["duracion_imputada"])
    return salida


# ---------------------------------------------------------------- recurrencia por sitio (F2, sección 4.4)
FIN_OCTUBRE = pd.Timestamp("2026-11-01")   # el uptime de octubre cuenta hasta el 31-10 a las 23:59


def minutos_reales(inicios, cierres, fusionar=utilidades.fusionar_intervalos_iterativo):
    """Minutos fuera de servicio sin contar dos veces los traslapes.

    `fusionar` es la función que une los intervalos. Desde la Fase 3 se usa la iterativa: da el mismo
    resultado que la recursiva de la Fase 2, es más rápida y no tiene límite de profundidad (la
    recursiva falla con RecursionError sobre unos 1.000 intervalos de un mismo sitio).
    """
    intervalos = list(zip(inicios, cierres))
    return sum((fin - ini).total_seconds() / 60 for ini, fin in fusionar(intervalos))


def por_sitio(df):
    """Una fila por cada sitio de cada incidencia (separa las celdas con varios sitios)."""
    return df.assign(sitio=df["sitios"].map(utilidades.separar_sitios)).explode("sitio")


def tabla_recurrencia(df, fusionar=utilidades.fusionar_intervalos_iterativo):
    """Una fila por sitio: fallas TX con pérdida de servicio, minutos sumados y minutos reales (solo octubre)."""
    foco = por_sitio(df[(df["es_tx"] == 1) & (df["afecta_uptime"] == 1)])
    con_cierre = foco.dropna(subset=["fecha_cierre"]).copy()
    con_cierre["cierre_octubre"] = con_cierre["fecha_cierre"].clip(upper=FIN_OCTUBRE)
    tabla = foco.groupby("sitio").agg(
        fallas=("tt", "size"),
        fallas_p3e=("criticidad", lambda s: int((s == "P3E").sum())),
        abiertas=("fecha_cierre", lambda s: int(s.isna().sum())),
        enlace_principal=("tipo_enlace", lambda s: s.value_counts().index[0]),
        proveedor_tx=("proveedor_tx_1", lambda s: s.value_counts().index[0] if s.notna().any() else "Sin dato"),
        region=("region_principal", lambda s: s.value_counts().index[0] if s.notna().any() else "Sin dato"),
    )
    duracion_fechas = (con_cierre["cierre_octubre"] - con_cierre["fecha_inicio"]).dt.total_seconds() / 60
    tabla["minutos_sumados"] = duracion_fechas.groupby(con_cierre["sitio"]).sum()
    tabla["minutos_reales"] = pd.Series({sitio: minutos_reales(g["fecha_inicio"], g["cierre_octubre"], fusionar)
                                         for sitio, g in con_cierre.groupby("sitio")})
    tabla[["minutos_sumados", "minutos_reales"]] = tabla[["minutos_sumados", "minutos_reales"]].fillna(0).round(0)
    tabla["horas_fuera"] = (tabla["minutos_reales"] / 60).round(1)
    return tabla.sort_values(["fallas", "minutos_reales"], ascending=False).reset_index()


# ---------------------------------------------------------------- conjuntos de salida (F2, sección 5.1)
ID = "tt"
COLUMNAS_LIMPIO = [
    "tt", "sitios", "fecha_inicio", "fecha_cierre", "estado", "tipo_incidencia_noc", "incidencia_noc",
    "causa_raiz_noc", "criticidad", "criticidad_ord", "es_extendida", "impacto", "impacto_ord", "afecta_uptime", "es_tx",
    "tipo_enlace", "proveedor_tx_1", "codigo_servicio_tx_1", "proveedor", "duracion_min", "duracion_faltante",
    "cierre_invalido", "duracion_log", "q_sitios", "tiempo_respuesta_h", "hora_inicio", "dia_semana",
    "region_principal", "n_regiones", "comuna", "gestionable", "gestor_uptime", "titulo", "detalle",
]
COLUMNAS_MODELO = ["criticidad_ord", "es_extendida", "impacto_ord", "afecta_uptime", "es_tx", "duracion_faltante",
                   "cierre_invalido", "gestionable", "gestor_uptime", "hora_inicio", "dia_semana", "n_regiones",
                   "duracion_log_esc", "q_sitios_esc", "tiempo_respuesta_esc"]


def armar_conjuntos(df, columnas_onehot):
    """Separa el resultado en el conjunto limpio (legible) y el de modelo (solo números, sin vacíos)."""
    limpio = df[COLUMNAS_LIMPIO].copy()
    modelo = df[[ID] + COLUMNAS_MODELO + list(columnas_onehot)].copy()
    modelo[COLUMNAS_MODELO] = modelo[COLUMNAS_MODELO].astype(float)
    return limpio, modelo
