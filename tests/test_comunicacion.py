"""Pruebas del módulo de comunicación (Fase 4): casos normales, límite y de excepción.

Se ejecutan junto con las de la Fase 3, con el mismo comando desde la raíz del proyecto:

    .venv\\Scripts\\python.exe -m unittest discover -s tests -v       (Windows)
    .venv/bin/python -m unittest discover -s tests -v                (macOS y Linux)

Las tablas son pequeñas y hechas a mano, de modo que el resultado correcto se conoce de antemano.
"""
import sys
import tempfile
import unittest
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src import comunicacion as com                                       # noqa: E402


def tabla_sitios():
    """Cuatro sitios: dos recurrentes y dos con una sola falla."""
    return pd.DataFrame({
        "sitio": ["S1", "S2", "S3", "S4"],
        "fallas": [3, 1, 3, 1],
        "fallas_p3e": [1, 0, 0, 0],
        "abiertas": [0, 0, 0, 0],
        "enlace_principal": ["Microondas", "Fibra proveedor", "Fibra proveedor", "Microondas"],
        "proveedor_tx": ["WOM", "GTD", "GTD", "WOM"],
        "region": ["RM", "RM", "V", "V"],
        "minutos_sumados": [600.0, 60.0, 300.0, 30.0],
        "minutos_reales": [480.0, 60.0, 300.0, 30.0],
        "horas_fuera": [8.0, 1.0, 5.0, 0.5],
    })


class PruebasConcentracion(unittest.TestCase):
    def test_normal_curva_conocida(self):
        curva = com.concentracion([1, 3, 6])           # ordenados: 6, 3, 1 de un total de 10
        self.assertEqual(curva["parte_acumulada"].round(2).tolist(), [0.6, 0.9, 1.0])
        self.assertEqual(curva["parte_elementos"].round(4).tolist(), [0.3333, 0.6667, 1.0])

    def test_normal_ingenua_igual_a_vectorizada(self):
        valores = [5.5, 0.0, 2.25, 9.0, 1.0, 1.0]
        pd.testing.assert_frame_equal(com.concentracion(valores), com.concentracion_ingenua(valores))

    def test_normal_parte_del_total(self):
        curva = com.concentracion([10, 0, 0, 0, 0])     # un solo elemento concentra todo
        self.assertEqual(com.parte_del_total(curva, 0.2), 1.0)

    def test_limite_un_solo_valor(self):
        curva = com.concentracion([7])
        self.assertEqual(curva["parte_acumulada"].tolist(), [1.0])

    def test_limite_valores_iguales_dan_la_diagonal(self):
        curva = com.concentracion([2, 2, 2, 2])
        self.assertTrue((curva["parte_acumulada"] == curva["parte_elementos"]).all())

    def test_excepcion_sin_valores(self):
        with self.assertRaises(ValueError):
            com.concentracion([])
        with self.assertRaises(ValueError):
            com.concentracion_ingenua([])

    def test_excepcion_total_cero(self):
        with self.assertRaises(ValueError):
            com.concentracion([0, 0])

    def test_excepcion_parte_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            com.parte_del_total(com.concentracion([1, 2]), 0)


class PruebasResumenYPrioridad(unittest.TestCase):
    def test_normal_resumen_por_enlace(self):
        resumen = com.resumen_por(tabla_sitios(), "enlace_principal")
        self.assertEqual(resumen.loc["Microondas", "fallas"], 4)
        self.assertAlmostEqual(resumen.loc["Microondas", "horas"], 8.5)
        self.assertAlmostEqual(resumen["parte_horas"].sum(), 1.0)
        self.assertEqual(resumen.index[0], "Microondas")          # ordenado por horas

    def test_normal_prioridad_desempata_por_minutos(self):
        lista = com.lista_prioridad(tabla_sitios(), n=5)
        self.assertEqual(lista["sitio"].tolist(), ["S1", "S3"])  # 3 fallas cada uno; S1 suma más minutos

    def test_limite_nadie_es_recurrente(self):
        lista = com.lista_prioridad(tabla_sitios(), minimo_fallas=10)
        self.assertTrue(lista.empty)

    def test_excepcion_columna_inexistente(self):
        with self.assertRaises(KeyError):
            com.resumen_por(tabla_sitios(), "no_existe")

    def test_excepcion_n_invalido(self):
        with self.assertRaises(ValueError):
            com.lista_prioridad(tabla_sitios(), n=0)


class PruebasContratoYCarga(unittest.TestCase):
    def test_normal_contrato_cumplido(self):
        self.assertTrue(all(com.verificar_recurrencia(tabla_sitios()).values()))

    def test_limite_detecta_minutos_reales_mayores(self):
        tabla = tabla_sitios()
        tabla.loc[0, "minutos_reales"] = 9999
        controles = com.verificar_recurrencia(tabla)
        self.assertFalse(controles["Minutos reales no superan los sumados"])

    def test_excepcion_falta_columna(self):
        with self.assertRaises(KeyError):
            com.verificar_recurrencia(tabla_sitios().drop(columns="horas_fuera"))

    def test_excepcion_carpeta_sin_artefactos(self):
        with tempfile.TemporaryDirectory() as vacia:
            with self.assertRaises(FileNotFoundError):
                com.cargar_artefactos(vacia)


if __name__ == "__main__":
    unittest.main()
