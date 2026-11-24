"""Comunicación de resultados (Fase 4): de las tablas de la Fase 3 a las cifras que responden los objetivos.

La Fase 4 no vuelve a limpiar ni a transformar. Lee lo que la Fase 3 dejó en data/processed y trabaja
sobre las dos tablas interpretables (incidencias_limpio y recurrencia_tx_por_sitio), que conservan las
categorías y las unidades originales. El conjunto de modelo (incidencias_modelo) queda fuera: tiene
columnas 0/1 y valores escalados, que sirven para un modelo pero no se entienden en un gráfico.

Las funciones son de una sola tarea y no guardan estado entre llamadas; por eso son funciones y no
clases (el criterio de la Fase 3: una clase solo cuando el paso aprende algo y debe recordarlo).
"""
from pathlib import Path

import numpy as np
import pandas as pd

ARTEFACTOS = {
    "limpio": "incidencias_limpio.csv",
    "recurrencia": "recurrencia_tx_por_sitio.csv",
    "diccionario": "diccionario_f3.csv",
    "parametros": "parametros_f3.csv",
}
FECHAS = ["fecha_inicio", "fecha_cierre"]
COLUMNAS_RECURRENCIA = ["sitio", "fallas", "fallas_p3e", "abiertas", "enlace_principal", "proveedor_tx",
                        "region", "minutos_sumados", "minutos_reales", "horas_fuera"]


def cargar_artefactos(carpeta):
    """Lee los cuatro archivos que entrega la Fase 3. Si falta alguno, se detiene y dice qué ejecutar.

    La Fase 4 no inventa datos para poder seguir: un gráfico hecho sin los datos reales no responde nada.
    """
    carpeta = Path(carpeta)
    faltan = [archivo for archivo in ARTEFACTOS.values() if not (carpeta / archivo).is_file()]
    if faltan:
        raise FileNotFoundError(f"Faltan archivos de la Fase 3 en {carpeta}: {faltan}. "
                                "Ejecute antes los notebooks F2 y F3, que los escriben en data/processed.")
    tablas = {nombre: pd.read_csv(carpeta / archivo) for nombre, archivo in ARTEFACTOS.items()}
    for columna in FECHAS:                       # el CSV guarda las fechas como texto
        tablas["limpio"][columna] = pd.to_datetime(tablas["limpio"][columna])
    return tablas


def verificar_recurrencia(tabla):
    """Comprueba el contrato de la tabla por sitio antes de graficarla. Devuelve {control: True/False}.

    Cada control es una regla que debe cumplirse si la Fase 2 calculó bien: un sitio por fila, al menos
    una falla por sitio, los minutos reales nunca superan a los sumados (los traslapes solo pueden
    restar) y las horas son los minutos reales divididos por 60.
    """
    faltan = [c for c in COLUMNAS_RECURRENCIA if c not in tabla.columns]
    if faltan:
        raise KeyError(f"La tabla de recurrencia no tiene las columnas {faltan}")
    return {
        "Un sitio por fila": bool(tabla["sitio"].is_unique),
        "Cada sitio tiene al menos una falla": bool((tabla["fallas"] >= 1).all()),
        "Fallas P3E no superan las fallas": bool((tabla["fallas_p3e"] <= tabla["fallas"]).all()),
        "Minutos reales no superan los sumados": bool((tabla["minutos_reales"] <= tabla["minutos_sumados"]).all()),
        "Horas = minutos reales / 60": bool(np.allclose(tabla["horas_fuera"], tabla["minutos_reales"] / 60, atol=0.05)),
        "Sin vacíos en las columnas que se grafican": bool(tabla[["fallas", "horas_fuera", "enlace_principal",
                                                                  "proveedor_tx"]].notna().all().all()),
    }


def concentracion(valores):
    """Curva de concentración (Pareto): qué parte del total acumulan los k primeros, para cada k.

    Ordena de mayor a menor y acumula con np.cumsum: O(n log n) por el orden y O(n) para acumular.
    Devuelve una tabla con la parte de los elementos (eje x) y la parte del total que acumulan (eje y).
    """
    v = np.sort(np.asarray(valores, dtype=float))[::-1]
    if v.size == 0:
        raise ValueError("No hay valores para calcular la concentración.")
    if v.sum() <= 0:
        raise ValueError("El total es cero: la concentración no está definida.")
    return pd.DataFrame({"parte_elementos": np.arange(1, v.size + 1) / v.size,
                         "parte_acumulada": np.cumsum(v) / v.sum()})


def concentracion_ingenua(valores):
    """Misma curva que `concentracion`, pero suma desde cero el prefijo de cada k: O(n²).

    Es la forma en que se escribiría «para cada k, sumar los k mayores». Se conserva solo para medir.
    """
    v = sorted((float(x) for x in valores), reverse=True)
    if not v:
        raise ValueError("No hay valores para calcular la concentración.")
    total = sum(v)
    if total <= 0:
        raise ValueError("El total es cero: la concentración no está definida.")
    n = len(v)
    return pd.DataFrame({"parte_elementos": [(k + 1) / n for k in range(n)],
                         "parte_acumulada": [sum(v[:k + 1]) / total for k in range(n)]})


def parte_del_total(curva, parte_elementos):
    """Qué parte del total acumula la fracción `parte_elementos` de los elementos (por ejemplo, el 20 %)."""
    if not 0 < parte_elementos <= 1:
        raise ValueError("parte_elementos debe estar entre 0 y 1.")
    fila = curva[curva["parte_elementos"] >= parte_elementos - 1e-12].iloc[0]
    return float(fila["parte_acumulada"])


def resumen_por(tabla, columna):
    """Sitios, fallas y horas fuera de servicio por categoría (tipo de enlace, proveedor, región).

    Agrega la parte del total de fallas y de horas, y las horas por falla, que es la cifra que separa
    «falla mucho» de «cuando falla, dura mucho».
    """
    if columna not in tabla.columns:
        raise KeyError(f"No existe la columna {columna!r}")
    resumen = tabla.groupby(columna).agg(sitios=("sitio", "size"), fallas=("fallas", "sum"),
                                         horas=("horas_fuera", "sum"))
    resumen["parte_fallas"] = resumen["fallas"] / resumen["fallas"].sum()
    resumen["parte_horas"] = resumen["horas"] / resumen["horas"].sum()
    resumen["horas_por_falla"] = resumen["horas"] / resumen["fallas"]
    return resumen.sort_values("horas", ascending=False)


def lista_prioridad(tabla, n=10, minimo_fallas=2):
    """Los n sitios recurrentes que encabezan la lista de escalamiento.

    Usa el orden que definió la Fase 2 (objetivo específico 4): primero más fallas en el mes y, a igual
    número de fallas, más minutos fuera de servicio. Se ordena aquí de nuevo para no depender del orden
    del archivo.
    """
    if n < 1:
        raise ValueError("n debe ser al menos 1.")
    recurrentes = tabla[tabla["fallas"] >= minimo_fallas]
    orden = recurrentes.sort_values(["fallas", "minutos_reales"], ascending=False, kind="stable")
    return orden.head(n).reset_index(drop=True)


def puntaje_prioridad(tabla, peso_fallas=0.5, minimo_fallas=2):
    """Lista de escalamiento con un criterio de pesos explícito y reproducible.

    Cada sitio recurrente recibe dos posiciones relativas entre 0 y 1 (percentiles): una por número de
    fallas y otra por minutos reales fuera de servicio. El puntaje es
        peso_fallas · percentil_fallas + (1 − peso_fallas) · percentil_minutos.
    Se usan percentiles y no los valores directos porque los minutos tienen un sitio de 660 horas que,
    sin esta conversión, decidiría la lista casi solo. Con peso_fallas = 1 se ordena solo por fallas y
    con 0 solo por minutos. A igual puntaje desempata el orden oficial (fallas y luego minutos).
    """
    if not 0 <= peso_fallas <= 1:
        raise ValueError("peso_fallas debe estar entre 0 y 1.")
    recurrentes = tabla[tabla["fallas"] >= minimo_fallas].copy()
    if recurrentes.empty:
        raise ValueError(f"No hay sitios con {minimo_fallas} o más fallas.")
    recurrentes["percentil_fallas"] = recurrentes["fallas"].rank(pct=True)
    recurrentes["percentil_minutos"] = recurrentes["minutos_reales"].rank(pct=True)
    recurrentes["puntaje"] = (peso_fallas * recurrentes["percentil_fallas"]
                              + (1 - peso_fallas) * recurrentes["percentil_minutos"])
    orden = recurrentes.sort_values(["puntaje", "fallas", "minutos_reales"], ascending=False, kind="stable")
    return orden.reset_index(drop=True)


def sensibilidad_prioridad(tabla, pesos=(0.0, 0.25, 0.5, 0.75, 1.0), n=10, minimo_fallas=2):
    """Prueba de sensibilidad: ¿cambian los n primeros de la lista oficial si se mueven los pesos?

    Para cada peso de las fallas cuenta cuántos de los n sitios de `lista_prioridad` siguen entre los
    n primeros de `puntaje_prioridad`. Si coinciden casi todos, la lista no depende del peso elegido.
    """
    oficial = set(lista_prioridad(tabla, n, minimo_fallas)["sitio"])
    filas = []
    for peso in pesos:
        primeros = puntaje_prioridad(tabla, peso, minimo_fallas).head(n)["sitio"]
        filas.append({"peso_fallas": peso, "peso_minutos": round(1 - peso, 2),
                      "coinciden_con_oficial": len(oficial & set(primeros)), "de": n,
                      "primeros_3": ", ".join(primeros.head(3))})
    return pd.DataFrame(filas)


def sitios_estables(tabla, pesos=(0.0, 0.25, 0.5, 0.75, 1.0), n=10, minimo_fallas=2):
    """Sitios que están entre los n primeros de la lista oficial y de TODAS las listas con pesos."""
    estables = set(lista_prioridad(tabla, n, minimo_fallas)["sitio"])
    for peso in pesos:
        estables &= set(puntaje_prioridad(tabla, peso, minimo_fallas).head(n)["sitio"])
    orden = lista_prioridad(tabla, len(tabla), minimo_fallas)["sitio"]
    return [sitio for sitio in orden if sitio in estables]


def resumen_abiertas(tabla):
    """Incidencias que seguían abiertas al cierre de octubre (objetivo 1).

    Se informan aparte porque una incidencia abierta no tiene fecha de cierre y no suma minutos: sin
    esta cifra, un sitio con incidencias abiertas parecería haber estado menos tiempo fuera de servicio.
    """
    if "abiertas" not in tabla.columns:
        raise KeyError("La tabla no tiene la columna 'abiertas'.")
    con_abiertas = tabla[tabla["abiertas"] > 0]
    return {"sitios_con_abiertas": int(len(con_abiertas)),
            "incidencias_abiertas": int(tabla["abiertas"].sum()),
            "parte_sitios": float(len(con_abiertas) / len(tabla)) if len(tabla) else 0.0,
            "sitios": con_abiertas["sitio"].tolist()}


def fallas_por_dia(limpio, sitios):
    """Matriz sitio × día de octubre con el número de fallas TX que afectan el uptime (mapa de calor).

    Usa el mismo filtro que la tabla de recurrencia (es_tx = 1 y afecta_uptime = 1) y separa los
    sitios de cada incidencia con `limpieza.por_sitio`, así la suma de cada fila coincide con la columna
    `fallas` de la tabla de recurrencia. Las filas siguen el orden de `sitios`.
    """
    from .limpieza import por_sitio            # import local: limpieza no depende de este módulo
    foco = por_sitio(limpio[(limpio["es_tx"] == 1) & (limpio["afecta_uptime"] == 1)])
    foco = foco[foco["sitio"].isin(sitios)]
    dias = pd.Series(range(1, 32), name="dia")
    matriz = (foco.assign(dia=foco["fecha_inicio"].dt.day)
                  .groupby(["sitio", "dia"]).size().unstack(fill_value=0)
                  .reindex(index=list(sitios), columns=dias, fill_value=0))
    return matriz


def guardar_figura(figura, carpeta, nombre, dpi=200):
    """Guarda la figura en PNG a `dpi` puntos por pulgada (suficiente para el informe) y devuelve la ruta."""
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{nombre}.png"
    figura.savefig(ruta, dpi=dpi, bbox_inches="tight", facecolor="white")
    return ruta
