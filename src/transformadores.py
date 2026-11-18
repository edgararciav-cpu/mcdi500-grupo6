"""Transformadores: los pasos del pipeline que APRENDEN algo de los datos.

Criterio (guía del docente): un paso es clase solo si necesita recordar algo entre ajustar y
transformar. Aquí cada clase aprende un parámetro de los datos:

    UnificadorVariantes     la escritura más frecuente de cada categoría
    EliminadorCasiVacias    qué columnas superan el umbral de vacíos
    ImputadorMedianaGrupo   la mediana de cada grupo y la mediana general
    CodificadorNominal      el vocabulario de categorías (y cuáles son poco frecuentes)
    Escalador               los parámetros de la escala (media y desviación, o mínimo y máximo)

Las operaciones que no aprenden nada siguen siendo funciones (módulo limpieza). PasoFijo las
envuelve para que el Pipeline pueda recorrer todos los pasos de la misma forma.

Principios de la POO en este módulo:
    herencia         todas las clases heredan de Transformador el control de estado y la validación
    polimorfismo     el Pipeline llama ajustar() y transformar() sin saber de qué clase es cada paso
    encapsulamiento  lo aprendido vive en _parametros (con guion bajo) y solo se lee con una copia
"""
import copy

import pandas as pd
from sklearn.base import clone
from sklearn.preprocessing import MinMaxScaler, OneHotEncoder, RobustScaler, StandardScaler

from . import utilidades


class Transformador:
    """Clase base: el contrato común de todos los pasos del pipeline. No se usa directamente.

    Define QUÉ métodos tiene un paso y CÓMO se controla su estado; las clases hijas solo
    implementan aprender() y aplicar(), que es lo que cambia de un paso a otro.
    """

    def __init__(self, columnas=()):
        # columnas que el paso necesita en la tabla; acepta un nombre o una lista
        self.columnas = [columnas] if isinstance(columnas, str) else list(columnas)
        self._parametros = {}       # lo que el paso aprende de los datos (estado interno)
        self._ajustado = False      # impide transformar antes de ajustar

    @property
    def nombre(self):
        """Nombre legible del paso: la clase real del objeto y sus columnas."""
        detalle = ", ".join(self.columnas)
        return f"{type(self).__name__}({detalle})" if detalle else type(self).__name__

    @property
    def parametros(self):
        """Copia de lo aprendido: quien la recibe no puede alterar el estado interno (copia defensiva)."""
        return copy.deepcopy(self._parametros)

    @property
    def ajustado(self):
        return self._ajustado

    def ajustar(self, df):
        """Aprende los parámetros del conjunto que recibe. Devuelve self para poder encadenar."""
        faltan = [c for c in self.columnas if c not in df.columns]
        if faltan:
            raise KeyError(f"{self.nombre}: no existen las columnas {faltan}")
        self._parametros = self.aprender(df)
        self._ajustado = True
        return self

    def transformar(self, df):
        """Aplica lo aprendido sobre una copia: nunca modifica la tabla que recibe."""
        if not self._ajustado:
            raise RuntimeError(f"{self.nombre}: hay que ajustar antes de transformar.")
        return self.aplicar(df.copy())

    def ajustar_transformar(self, df):
        """Atajo para el caso habitual: aprender y aplicar sobre el mismo conjunto."""
        return self.ajustar(df).transformar(df)

    # ---- lo que cada clase hija DEBE implementar -------------------------------------------
    def aprender(self, df):
        raise NotImplementedError(f"{type(self).__name__} debe implementar aprender().")

    def aplicar(self, df):
        raise NotImplementedError(f"{type(self).__name__} debe implementar aplicar().")

    def __repr__(self):
        return f"{self.nombre} [{'ajustado' if self._ajustado else 'sin ajustar'}]"


class PasoFijo(Transformador):
    """Envuelve una función que no aprende nada (adaptador): permite que el Pipeline la trate como un paso más."""

    def __init__(self, funcion, **argumentos):
        super().__init__()
        self._funcion = funcion
        self._argumentos = argumentos

    @property
    def nombre(self):
        return f"PasoFijo({self._funcion.__name__})"

    def aprender(self, df):
        return {}                                   # no hay nada que aprender

    def aplicar(self, df):
        return self._funcion(df, **self._argumentos)


class UnificadorVariantes(Transformador):
    """Une las escrituras de una misma categoría ("Pendiente" y "PENDIENTE") en la más frecuente.

    Aprende qué columnas son categorías (hasta `max_categorias` valores distintos, sin el texto libre)
    y, para cada una, la escritura más frecuente de cada forma normalizada.
    """

    def __init__(self, excluir=(), max_categorias=500):
        super().__init__()
        self.excluir = list(excluir)
        self.max_categorias = max_categorias

    @staticmethod
    def _llave(serie):
        return serie.str.lower().str.replace(r"\s+", " ", regex=True)

    def aprender(self, df):
        categoricas = [c for c in df.columns if c not in self.excluir and df[c].nunique() <= self.max_categorias]
        formas = {}
        for col in categoricas:
            forma_frecuente = df[col].groupby(self._llave(df[col])).agg(lambda s: s.value_counts().index[0])
            formas[col] = forma_frecuente
        return {"formas": formas}

    def _unificar(self, serie, forma_frecuente):
        """Reescribe cada valor con la forma aprendida. Un valor que no se vio al ajustar se conserva tal cual."""
        aprendida = self._llave(serie).map(forma_frecuente)
        return aprendida.where(aprendida.notna(), serie).where(serie.notna())

    def aplicar(self, df):
        for col, forma_frecuente in self._parametros["formas"].items():
            if col in df.columns:
                df[col] = self._unificar(df[col], forma_frecuente)
        return df

    def cambios(self, df):
        """Cuántos valores reescribiría en cada columna (para la bitácora)."""
        conteo = {}
        for col, forma_frecuente in self._parametros["formas"].items():
            nueva = self._unificar(df[col], forma_frecuente)
            n = int((nueva != df[col])[df[col].notna()].sum())
            if n:
                conteo[col] = n
        return conteo


class EliminadorCasiVacias(Transformador):
    """Quita las columnas con más de `umbral` % de vacíos (salvo las que se conservan) y las fuera de alcance."""

    def __init__(self, umbral=95, conservar=(), fuera_de_alcance=()):
        super().__init__()
        self.umbral = umbral
        self.conservar = list(conservar)
        self.fuera_de_alcance = list(fuera_de_alcance)

    def aprender(self, df):
        pct_vacio = df.isna().mean() * 100
        casi_vacias = [c for c in pct_vacio[pct_vacio > self.umbral].index if c not in self.conservar]
        return {"casi_vacias": casi_vacias, "fuera_de_alcance": list(self.fuera_de_alcance)}

    def aplicar(self, df):
        quitar = self._parametros["casi_vacias"] + self._parametros["fuera_de_alcance"]
        faltan = [c for c in quitar if c not in df.columns]
        if faltan:                                  # mejor fallar que quitar otra cosa por un nombre mal escrito
            raise KeyError(f"{self.nombre}: no existen {faltan}")
        return df.drop(columns=quitar)


class ImputadorMedianaGrupo(Transformador):
    """Rellena los vacíos de una columna con la mediana de su grupo; si el grupo no tiene datos, con la general.

    Aprende las medianas en ajustar() y las aplica en transformar(): en un conjunto nuevo se usan las
    medianas del ajuste, no las del conjunto nuevo (así no se filtra información de prueba).
    El resultado va a `destino`; la columna original no se toca, porque el conjunto limpio la conserva vacía.
    """

    def __init__(self, columna, grupos, destino):
        super().__init__([columna, *grupos])
        self.columna, self.grupos, self.destino = columna, list(grupos), destino

    def aprender(self, df):
        medianas = df.groupby(self.grupos)[self.columna].median()
        return {"por_grupo": medianas, "general": float(df[self.columna].median())}

    def aplicar(self, df):
        llaves = pd.MultiIndex.from_frame(df[self.grupos]) if len(self.grupos) > 1 else df[self.grupos[0]]
        mediana_grupo = pd.Series(self._parametros["por_grupo"].reindex(llaves).to_numpy(), index=df.index)
        df[self.destino] = df[self.columna].fillna(mediana_grupo).fillna(self._parametros["general"])
        return df


class CodificadorNominal(Transformador):
    """One-hot de variables nominales: una columna 0/1 por categoría.

    Usa el OneHotEncoder de scikit-learn como motor (adaptador): esta clase aporta el contrato
    ajustar/transformar del proyecto, los nombres de columna normalizados y el vacío como "Sin dato".
    Con `frec_minima` las categorías con menos de ese porcentaje de filas se agrupan en una sola columna.
    """

    def __init__(self, columnas, frec_minima=None):
        super().__init__(columnas)
        self.frec_minima = frec_minima

    def aprender(self, df):
        motor = OneHotEncoder(min_frequency=self.frec_minima, handle_unknown="infrequent_if_exist",
                              sparse_output=False)
        motor.fit(df[self.columnas].fillna("Sin dato"))
        nombres = [utilidades.normalizar_nombre(n) for n in motor.get_feature_names_out(self.columnas)]
        return {"motor": motor, "columnas_nuevas": nombres}

    def aplicar(self, df):
        valores = self._parametros["motor"].transform(df[self.columnas].fillna("Sin dato")).astype(int)
        nuevas = pd.DataFrame(valores, columns=self._parametros["columnas_nuevas"], index=df.index)
        return pd.concat([df, nuevas], axis=1)

    @property
    def columnas_nuevas(self):
        return list(self._parametros.get("columnas_nuevas", []))


# ---- Strategy: el Escalador recibe la forma de escalar como un objeto intercambiable ------------
ESTRATEGIAS = {"estandar": StandardScaler, "minmax": MinMaxScaler, "robusta": RobustScaler}


def crear_estrategia(nombre):
    """Devuelve una estrategia de escala nueva a partir de su nombre ("estandar", "minmax" o "robusta")."""
    if nombre not in ESTRATEGIAS:
        raise utilidades.ProyectoError(f"estrategia de escala desconocida: {nombre!r}; use {sorted(ESTRATEGIAS)}")
    return ESTRATEGIAS[nombre]()


class Escalador(Transformador):
    """Escala una columna numérica y deja el resultado en `destino`.

    Patrón Strategy: la forma de escalar es un objeto que se pasa al construir (estándar, mín-máx o
    robusta). Cambiar de estrategia no obliga a cambiar esta clase ni el pipeline.
    """

    def __init__(self, columna, destino, estrategia="estandar"):
        super().__init__(columna)
        self.columna, self.destino = columna, destino
        self.estrategia = crear_estrategia(estrategia) if isinstance(estrategia, str) else estrategia

    @property
    def nombre(self):
        return f"Escalador({self.columna}, {type(self.estrategia).__name__})"

    def aprender(self, df):
        motor = clone(self.estrategia).fit(df[[self.columna]])     # clone: cada ajuste parte de cero
        return {"motor": motor}

    def aplicar(self, df):
        df[self.destino] = self._parametros["motor"].transform(df[[self.columna]]).ravel()
        return df
