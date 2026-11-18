"""Núcleo del proyecto MCDI500 · Fallas recurrentes de transmisión (Grupo 6).

Módulos:
    utilidades       funciones base de las Fases 1 y 2 (texto, duraciones, sitios, fusión recursiva)
    carga            lee el archivo de data/raw y verifica que sea el que registró la Fase 1
    limpieza         operaciones que NO aprenden de los datos (funciones)
    transformadores  pasos que SÍ aprenden de los datos (clases con ajustar y transformar)
    pipeline         encadena los pasos y ejecuta toda la Fase 2 con una sola llamada
    medicion         mide tiempo y memoria para comparar implementaciones

Desde un notebook, con la raíz del proyecto en sys.path:
    from src.pipeline import ejecutar
"""
