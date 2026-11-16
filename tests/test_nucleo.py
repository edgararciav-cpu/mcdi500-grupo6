"""Pruebas del núcleo de la Fase 3: casos normales, límite y de excepción.

Se ejecutan con un solo comando desde la raíz del proyecto, sin instalar nada más (unittest viene con Python):

    .venv\\Scripts\\python.exe -m unittest discover -s tests -v       (Windows)
    .venv/bin/python -m unittest discover -s tests -v                (macOS y Linux)

Cada prueba usa una tabla pequeña construida a mano, donde el resultado correcto se conoce de antemano.
La última clase comprueba, con los datos reales, que el pipeline con clases produce los mismos archivos
que la Fase 2.
"""
import hashlib
import random
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src import limpieza, utilidades                                       # noqa: E402
from src.medicion import comparar                                         # noqa: E402
from src.pipeline import Bitacora, Pipeline, ejecutar                     # noqa: E402
from src.transformadores import (CodificadorNominal, EliminadorCasiVacias, Escalador,   # noqa: E402
                                 ImputadorMedianaGrupo, PasoFijo, Transformador, UnificadorVariantes)


class PruebasTransformadorBase(unittest.TestCase):
    def test_excepcion_transformar_sin_ajustar(self):
        with self.assertRaises(RuntimeError):
            Escalador("x", "x_esc").transformar(pd.DataFrame({"x": [1.0, 2.0]}))

    def test_excepcion_columna_inexistente(self):
        with self.assertRaises(KeyError):
            Escalador("no_existe", "z").ajustar(pd.DataFrame({"x": [1.0]}))

    def test_excepcion_clase_base_sin_implementar(self):
        with self.assertRaises(NotImplementedError):
            Transformador().ajustar(pd.DataFrame({"x": [1]}))

    def test_limite_copia_defensiva_y_entrada_intacta(self):
        df = pd.DataFrame({"x": [1.0, np.nan], "g": ["a", "a"]})
        paso = ImputadorMedianaGrupo("x", ["g"], "x_imp").ajustar(df)
        paso.parametros["general"] = 999                     # se modifica la copia, no el objeto
        self.assertEqual(paso.parametros["general"], 1.0)
        paso.transformar(df)
        self.assertNotIn("x_imp", df.columns)                # la tabla original no cambió


class PruebasImputador(unittest.TestCase):
    def test_normal_mediana_de_su_grupo(self):
        df = pd.DataFrame({"x": [1.0, 3.0, np.nan, 10.0, np.nan], "g": ["a", "a", "a", "b", "b"]})
        salida = ImputadorMedianaGrupo("x", ["g"], "x_imp").ajustar_transformar(df)
        self.assertEqual(salida["x_imp"].tolist(), [1.0, 3.0, 2.0, 10.0, 10.0])

    def test_limite_sin_vacios_no_cambia_nada(self):
        df = pd.DataFrame({"x": [1.0, 2.0], "g": ["a", "b"]})
        salida = ImputadorMedianaGrupo("x", ["g"], "x_imp").ajustar_transformar(df)
        self.assertEqual(salida["x_imp"].tolist(), [1.0, 2.0])

    def test_limite_grupo_sin_datos_usa_la_mediana_general(self):
        df = pd.DataFrame({"x": [1.0, 3.0, np.nan], "g": ["a", "a", "z"]})
        salida = ImputadorMedianaGrupo("x", ["g"], "x_imp").ajustar_transformar(df)
        self.assertEqual(salida["x_imp"].iloc[2], 2.0)

    def test_normal_usa_lo_aprendido_en_un_conjunto_nuevo(self):
        entrenamiento = pd.DataFrame({"x": [1.0, 3.0], "g": ["a", "a"]})
        prueba = pd.DataFrame({"x": [np.nan], "g": ["a"]})
        paso = ImputadorMedianaGrupo("x", ["g"], "x_imp").ajustar(entrenamiento)
        self.assertEqual(paso.transformar(prueba)["x_imp"].iloc[0], 2.0)


class PruebasUnificadorYEliminador(unittest.TestCase):
    def test_normal_escritura_mas_frecuente(self):
        df = pd.DataFrame({"estado": ["Pendiente", "Pendiente", "PENDIENTE", "Cerrada"]})
        salida = UnificadorVariantes().ajustar_transformar(df)
        self.assertEqual(salida["estado"].tolist(), ["Pendiente", "Pendiente", "Pendiente", "Cerrada"])

    def test_limite_una_sola_categoria(self):
        df = pd.DataFrame({"estado": ["Cerrada", "Cerrada"]})
        self.assertEqual(UnificadorVariantes().ajustar_transformar(df)["estado"].tolist(), ["Cerrada", "Cerrada"])

    def test_limite_el_texto_libre_no_se_toca(self):
        df = pd.DataFrame({"detalle": ["Hola", "HOLA"]})
        salida = UnificadorVariantes(excluir=["detalle"]).ajustar_transformar(df)
        self.assertEqual(salida["detalle"].tolist(), ["Hola", "HOLA"])

    def test_limite_categoria_que_no_se_vio_al_ajustar_se_conserva(self):
        paso = UnificadorVariantes().ajustar(pd.DataFrame({"q": ["1", "2", "2"]}))
        self.assertEqual(paso.transformar(pd.DataFrame({"q": ["2", "21", None]}))["q"].tolist()[:2], ["2", "21"])

    def test_normal_quita_las_casi_vacias_y_conserva_las_pedidas(self):
        df = pd.DataFrame({"llena": [1, 2, 3], "vacia": [np.nan] * 3, "necesaria": [np.nan] * 3})
        salida = EliminadorCasiVacias(umbral=95, conservar=["necesaria"]).ajustar_transformar(df)
        self.assertEqual(list(salida.columns), ["llena", "necesaria"])

    def test_excepcion_columna_fuera_de_alcance_inexistente(self):
        with self.assertRaises(KeyError):
            EliminadorCasiVacias(fuera_de_alcance=["no_existe"]).ajustar_transformar(pd.DataFrame({"a": [1]}))


class PruebasCodificadorYEscalador(unittest.TestCase):
    def test_normal_one_hot_suma_uno_y_vacio_es_sin_dato(self):
        df = pd.DataFrame({"color": ["rojo", "azul", None]})
        paso = CodificadorNominal(["color"])
        salida = paso.ajustar_transformar(df)
        self.assertTrue((salida[paso.columnas_nuevas].sum(axis=1) == 1).all())
        self.assertIn("color_sin_dato", paso.columnas_nuevas)

    def test_limite_frecuencia_minima_agrupa_las_raras(self):
        df = pd.DataFrame({"c": ["a"] * 99 + ["b"]})
        paso = CodificadorNominal(["c"], frec_minima=0.05)
        paso.ajustar(df)
        self.assertEqual(paso.columnas_nuevas, ["c_a", "c_infrequent_sklearn"])

    def test_normal_escala_estandar_media_cero(self):
        salida = Escalador("x", "x_esc", "estandar").ajustar_transformar(pd.DataFrame({"x": [1.0, 2.0, 3.0]}))
        self.assertAlmostEqual(salida["x_esc"].mean(), 0.0)

    def test_limite_minmax_entre_cero_y_uno(self):
        salida = Escalador("x", "x_esc", "minmax").ajustar_transformar(pd.DataFrame({"x": [5.0, 7.0, 9.0]}))
        self.assertEqual(salida["x_esc"].tolist(), [0.0, 0.5, 1.0])

    def test_excepcion_estrategia_desconocida(self):
        with self.assertRaises(utilidades.ProyectoError):
            Escalador("x", "x_esc", "logaritmica")


class PruebasPipelineYFunciones(unittest.TestCase):
    def test_normal_polimorfismo_y_observador(self):
        bitacora = Bitacora()
        tubo = Pipeline([PasoFijo(lambda d: d.assign(y=d["x"] * 2)), Escalador("y", "y_esc", "minmax")], [bitacora])
        salida = tubo.ajustar_transformar(pd.DataFrame({"x": [1.0, 2.0, 3.0]}))
        self.assertEqual(salida["y_esc"].tolist(), [0.0, 0.5, 1.0])
        self.assertEqual(len(bitacora.tabla()), 2)           # el observador anotó los dos pasos

    def test_excepcion_paso_que_no_es_transformador(self):
        with self.assertRaises(TypeError):
            Pipeline().agregar(lambda d: d)

    def test_excepcion_pipeline_sin_ajustar(self):
        with self.assertRaises(RuntimeError):
            Pipeline([Escalador("x", "x_esc")]).transformar(pd.DataFrame({"x": [1.0]}))

    def test_excepcion_valor_fuera_del_orden_declarado(self):
        with self.assertRaises(utilidades.ProyectoError):
            limpieza.codificar_ordinal(pd.Series(["P1", "P9"], name="criticidad"), limpieza.ORDENES["criticidad"])

    def test_normal_p3_y_p3e_comparten_nivel(self):
        niveles = limpieza.codificar_ordinal(pd.Series(["P3", "P3E", "P1"]), limpieza.ORDENES["criticidad"])
        self.assertEqual(niveles.tolist(), [3, 3, 5])

    def test_normal_fusion_recursiva_e_iterativa_coinciden(self):
        azar = random.Random(42)
        for _ in range(200):
            intervalos = [(a, a + azar.randint(0, 20)) for a in (azar.randint(0, 100) for _ in range(azar.randint(0, 15)))]
            self.assertEqual(utilidades.fusionar_intervalos(intervalos), utilidades.fusionar_intervalos_iterativo(intervalos))

    def test_limite_y_excepcion_fusion(self):
        self.assertEqual(utilidades.fusionar_intervalos_iterativo([]), [])
        with self.assertRaises(utilidades.ProyectoError):
            utilidades.fusionar_intervalos_iterativo([(5, 1)])

    def test_normal_vacios_vectorizado_igual_al_de_la_fase_2(self):
        df = pd.DataFrame({"a": [" NA ", "x", "", "n/a", "No aplica"], "b": ["-", "0000-00-00 00:00:00", "y ", "z", "na"]})
        pd.testing.assert_frame_equal(limpieza.unificar_vacios(df), limpieza.unificar_vacios_por_celda(df))

    def test_limite_columna_sin_vacios_no_cambia(self):
        df = pd.DataFrame({"a": ["x", "y"]})
        pd.testing.assert_frame_equal(limpieza.unificar_vacios(df), df)

    def test_excepcion_comparacion_con_resultados_distintos(self):
        with self.assertRaises(AssertionError):
            comparar({"a": lambda: 1, "b": lambda: 2}, repeticiones=1)


class PruebaEquivalenciaConFase2(unittest.TestCase):
    """Con los datos reales: el pipeline con clases genera los mismos tres archivos que F2, byte a byte."""

    def test_normal_mismos_archivos_que_la_fase_2(self):
        resultado = ejecutar(RAIZ)
        archivos = {"limpio": "incidencias_limpio.csv", "modelo": "incidencias_modelo.csv",
                    "recurrencia": "recurrencia_tx_por_sitio.csv"}
        with tempfile.TemporaryDirectory() as carpeta:
            for clave, nombre in archivos.items():
                ruta = Path(carpeta) / nombre
                resultado[clave].to_csv(ruta, index=False, encoding="utf-8")
                huella_f3 = hashlib.sha256(ruta.read_bytes()).hexdigest()
                huella_f2 = hashlib.sha256((RAIZ / "data" / "processed" / nombre).read_bytes()).hexdigest()
                self.assertEqual(huella_f3, huella_f2, f"{nombre} cambió respecto de la Fase 2")


if __name__ == "__main__":
    unittest.main(verbosity=2)
