"""Medición de tiempo y memoria para comparar implementaciones de una misma operación.

Protocolo (guía del docente): las versiones deben dar el mismo resultado; se mide sobre los datos
reales, repitiendo varias veces y conservando el MENOR tiempo (los valores altos suelen deberse a que
el computador estaba haciendo otra cosa); la memoria se mide aparte con tracemalloc.
"""
import timeit
import tracemalloc

import pandas as pd


def tiempo_minimo(funcion, *args, repeticiones=7, **kwargs):
    """Menor tiempo (segundos) de `repeticiones` ejecuciones de funcion(*args, **kwargs)."""
    return min(timeit.repeat(lambda: funcion(*args, **kwargs), number=1, repeat=repeticiones))


def memoria_pico(funcion, *args, **kwargs):
    """Memoria máxima (MB) que reserva una ejecución de la función, medida con tracemalloc."""
    tracemalloc.start()
    try:
        funcion(*args, **kwargs)
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return pico / 1024 / 1024


def comparar(versiones, *args, iguales=None, repeticiones=7, **kwargs):
    """Mide varias versiones de la misma operación con los mismos argumentos.

    `versiones` es {nombre: función}. Antes de medir comprueba que todas den el mismo resultado
    (con `iguales(a, b)` si se entrega; si no, con ==). Devuelve una tabla con tiempo y memoria.
    """
    resultados = {nombre: f(*args, **kwargs) for nombre, f in versiones.items()}
    nombres = list(resultados)
    comparar_con = iguales or (lambda a, b: a == b)
    for otro in nombres[1:]:
        if not comparar_con(resultados[nombres[0]], resultados[otro]):
            raise AssertionError(f"«{otro}» no da el mismo resultado que «{nombres[0]}»: la comparación no sirve")
    filas = []
    for nombre, f in versiones.items():
        filas.append({"version": nombre,
                      "tiempo_min_s": tiempo_minimo(f, *args, repeticiones=repeticiones, **kwargs),
                      "memoria_pico_mb": memoria_pico(f, *args, **kwargs)})
    tabla = pd.DataFrame(filas).set_index("version")
    tabla["veces_mas_lenta"] = tabla["tiempo_min_s"] / tabla["tiempo_min_s"].min()
    return tabla
