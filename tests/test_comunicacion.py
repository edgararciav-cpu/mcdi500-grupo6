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

    def test_normal_suma_por_enlace_coincide_con_el_total(self):
        tabla = tabla_sitios()
        resumen = com.resumen_por(tabla, "enlace_principal")
        self.assertEqual(resumen["fallas"].sum(), tabla["fallas"].sum())
        self.assertAlmostEqual(resumen["horas"].sum(), tabla["horas_fuera"].sum())


def tabla_criterio():
    """Tres sitios recurrentes en los que fallas y minutos ordenan al revés, y uno con una sola falla."""
    return pd.DataFrame({
        "sitio": ["A", "B", "C", "D"],
        "fallas": [5, 3, 2, 1],
        "abiertas": [0, 1, 0, 2],
        "minutos_reales": [100.0, 500.0, 900.0, 5000.0],
    })


class PruebasCriterioYSensibilidad(unittest.TestCase):
    def test_normal_peso_uno_ordena_por_fallas(self):
        lista = com.puntaje_prioridad(tabla_criterio(), peso_fallas=1.0)
        self.assertEqual(lista["sitio"].tolist(), ["A", "B", "C"])

    def test_normal_peso_cero_ordena_por_minutos(self):
        lista = com.puntaje_prioridad(tabla_criterio(), peso_fallas=0.0)
        self.assertEqual(lista["sitio"].tolist(), ["C", "B", "A"])

    def test_normal_sitio_con_una_falla_no_entra_a_la_lista(self):
        # D tiene la mayor duración, pero una sola falla: no es recurrente con ninguno de los dos criterios
        self.assertNotIn("D", com.puntaje_prioridad(tabla_criterio(), 0.0)["sitio"].tolist())
        self.assertNotIn("D", com.lista_prioridad(tabla_criterio())["sitio"].tolist())

    def test_normal_sensibilidad_peso_uno_coincide_con_la_oficial(self):
        tabla = com.sensibilidad_prioridad(tabla_criterio(), pesos=(0.0, 1.0), n=1)
        self.assertEqual(tabla["coinciden_con_oficial"].tolist(), [0, 1])  # con peso 0 el primero es C, no A

    def test_limite_estables_cuando_todos_entran(self):
        # con n mayor que los recurrentes, todos están en todas las listas
        self.assertEqual(com.sitios_estables(tabla_criterio(), n=10), ["A", "B", "C"])

    def test_excepcion_peso_fuera_de_rango(self):
        with self.assertRaises(ValueError):
            com.puntaje_prioridad(tabla_criterio(), peso_fallas=1.5)

    def test_excepcion_nadie_es_recurrente(self):
        with self.assertRaises(ValueError):
            com.puntaje_prioridad(tabla_criterio(), minimo_fallas=10)

    def test_normal_resumen_abiertas(self):
        resumen = com.resumen_abiertas(tabla_criterio())
        self.assertEqual((resumen["sitios_con_abiertas"], resumen["incidencias_abiertas"]), (2, 3))
        self.assertEqual(resumen["sitios"], ["B", "D"])


class PruebasFallasPorDia(unittest.TestCase):
    def limpio(self):
        # la segunda incidencia afecta dos sitios (separados por dos espacios); la tercera no es TX
        return pd.DataFrame({
            "sitios": ["S1", "S1  S2", "S1", "S2"],
            "es_tx": [1, 1, 0, 1],
            "afecta_uptime": [1, 1, 1, 1],
            "fecha_inicio": pd.to_datetime(["2026-10-03 08:00", "2026-10-03 20:00", "2026-10-04 09:00", "2026-10-31 10:00"]),
        })

    def test_normal_cuenta_por_sitio_y_dia(self):
        matriz = com.fallas_por_dia(self.limpio(), ["S1", "S2"])
        self.assertEqual(matriz.shape, (2, 31))
        self.assertEqual(matriz.loc["S1", 3], 2)                 # dos fallas el día 3
        self.assertEqual(matriz.loc["S1", 4], 0)                 # la del día 4 no es TX
        self.assertEqual(matriz.loc["S2"].sum(), 2)

    def test_limite_sitio_sin_fallas_queda_en_cero(self):
        matriz = com.fallas_por_dia(self.limpio(), ["S1", "S9"])
        self.assertEqual(matriz.loc["S9"].sum(), 0)


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
