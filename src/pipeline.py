"""Pipeline: encadena los pasos y ejecuta toda la Fase 2 con una sola llamada.

    from src.pipeline import ejecutar
    resultado = ejecutar(RAIZ)        # {"limpio", "modelo", "recurrencia", "pipeline", "bitacora", ...}

Patrones de diseño:
    Pipeline (composición)  una lista ordenada de pasos que se recorren por igual (polimorfismo)
    Observer                la Bitacora se suscribe al Pipeline y anota cada paso sin que el paso lo sepa
    Strategy                el Escalador recibe la forma de escalar como un objeto (ver transformadores)
"""
import pandas as pd

from . import carga, limpieza
from .transformadores import (CodificadorNominal, EliminadorCasiVacias, Escalador, ImputadorMedianaGrupo,
                              PasoFijo, Transformador, UnificadorVariantes)


class Bitacora:
    """Observador del Pipeline: registra cada paso con la forma de la tabla antes y después."""

    def __init__(self):
        self._registros = []

    def notificar(self, orden, paso, antes, despues):
        self._registros.append({"orden": orden, "paso": paso.nombre, "clase": type(paso).__name__,
                                "aprende": not isinstance(paso, PasoFijo),
                                "filas_antes": len(antes), "filas_despues": len(despues),
                                "columnas_antes": antes.shape[1], "columnas_despues": despues.shape[1]})

    def tabla(self):
        return pd.DataFrame(self._registros)


class Pipeline:
    """Encadena transformadores y los ejecuta en orden. Avisa a sus observadores después de cada paso."""

    def __init__(self, pasos=None, observadores=None):
        self._pasos = []
        self._observadores = list(observadores or [])
        self._ajustado = False
        for paso in pasos or []:
            self.agregar(paso)

    def agregar(self, paso):
        if not isinstance(paso, Transformador):
            raise TypeError(f"Se esperaba un Transformador y se recibió {type(paso).__name__}.")
        self._pasos.append(paso)
        return self

    def suscribir(self, observador):
        self._observadores.append(observador)
        return self

    def _avisar(self, orden, paso, antes, despues):
        for observador in self._observadores:
            observador.notificar(orden, paso, antes, despues)

    def ajustar_transformar(self, df):
        """Ajusta cada paso con la salida del anterior y devuelve el resultado final."""
        intermedio = df
        for orden, paso in enumerate(self._pasos, start=1):
            salida = paso.ajustar_transformar(intermedio)      # polimorfismo: igual para todas las clases
            self._avisar(orden, paso, intermedio, salida)
            intermedio = salida
        self._ajustado = True
        return intermedio

    def ajustar(self, df):
        self.ajustar_transformar(df)
        return self

    def transformar(self, df):
        """Aplica los pasos ya ajustados a un conjunto nuevo (no vuelve a aprender nada)."""
        if not self._ajustado:
            raise RuntimeError("Pipeline: hay que ajustar antes de transformar.")
        resultado = df
        for paso in self._pasos:
            resultado = paso.transformar(resultado)
        return resultado

    @property
    def pasos(self):
        return tuple(self._pasos)

    def paso(self, clase, indice=0):
        """El paso número `indice` de una clase dada (para leer lo que aprendió)."""
        return [p for p in self._pasos if isinstance(p, clase)][indice]

    def resumen(self):
        return pd.DataFrame([{"orden": i, "paso": p.nombre, "clase": type(p).__name__,
                              "aprende de los datos": "no" if isinstance(p, PasoFijo) else "sí"}
                             for i, p in enumerate(self._pasos, start=1)])

    def __len__(self):
        return len(self._pasos)

    def __repr__(self):
        return f"Pipeline({len(self._pasos)} pasos, {'ajustado' if self._ajustado else 'sin ajustar'})"


# ---------------------------------------------------------------- la Fase 2, armada con clases
CONSERVAR = ["proveedor_tx_1", "codigo_servicio_tx_1", "proveedor", "causa_raiz_noc"]
FUERA_DE_ALCANCE = ["tipo_incidencia_gmi", "incidenca_gmi", "causa_raiz_gmi", "codigo_de_servicio"]
GRUPOS_IMPUTACION = ["tipo_incidencia_noc", "criticidad"]
FREC_MINIMA = 0.01


def construir_pipeline(observadores=None):
    """Los pasos de la Fase 2 en el mismo orden de F2_Preprocesamiento.ipynb."""
    return Pipeline([
        PasoFijo(limpieza.limpiar_nombres),                                       # 3.1 nombres
        PasoFijo(limpieza.reparar_texto),                                          # 3.2 tildes rotas
        PasoFijo(limpieza.unificar_vacios),                                        # 3.3 marcadores de vacío
        UnificadorVariantes(excluir=limpieza.TEXTO_LIBRE),                         # 3.3 variantes de escritura
        EliminadorCasiVacias(umbral=95, conservar=CONSERVAR, fuera_de_alcance=FUERA_DE_ALCANCE),   # 3.4
        PasoFijo(limpieza.convertir_tipos),                                        # 3.5 tipos
        ImputadorMedianaGrupo("duracion_min", GRUPOS_IMPUTACION, "duracion_imputada"),   # 3.6
        PasoFijo(limpieza.derivar_variables),                                      # 4.1 derivadas
        PasoFijo(limpieza.codificar_ordinales),                                    # 4.2 ordinales
        CodificadorNominal(["tipo_incidencia_noc", "estado", "region_principal"], FREC_MINIMA),   # 4.3
        CodificadorNominal(["tipo_enlace"], None),                                 # 4.3 sin agrupar: es el foco
        PasoFijo(limpieza.log_duracion_modelo),
        Escalador("duracion_log_modelo", "duracion_log_esc", "estandar"),          # 5 escalamiento
        Escalador("q_sitios", "q_sitios_esc", "minmax"),
        Escalador("tiempo_respuesta_h", "tiempo_respuesta_esc", "minmax"),
    ], observadores)


def ejecutar(raiz, crudo=None):
    """Ejecuta la Fase 2 completa: carga, pipeline, conjuntos de salida y tabla de recurrencia.

    Devuelve un diccionario con limpio, modelo, recurrencia, el pipeline ajustado, la bitácora y la huella
    SHA-256 de la entrada. Si se pasa `crudo`, no se vuelve a leer el archivo.
    """
    huella = None
    if crudo is None:
        crudo, huella = carga.cargar_crudo(raiz)
    bitacora = Bitacora()
    pipeline = construir_pipeline([bitacora])
    final = pipeline.ajustar_transformar(crudo)
    columnas_onehot = [c for p in pipeline.pasos if isinstance(p, CodificadorNominal) for c in p.columnas_nuevas]
    limpio, modelo = limpieza.armar_conjuntos(final, columnas_onehot)
    recurrencia = limpieza.tabla_recurrencia(final)
    return {"limpio": limpio, "modelo": modelo, "recurrencia": recurrencia, "final": final,
            "pipeline": pipeline, "bitacora": bitacora.tabla(), "huella_entrada": huella}
