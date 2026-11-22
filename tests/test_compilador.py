"""Casos de prueba automatizados (OE4). Ejecutar con:  python -m unittest -v"""
import random
import unittest

from app.services.analizador_service import compilar
from app.services.compilador import automatas, lexico

VALIDA = ("SI TIPO_LINEA == PREPAGO Y OPERADOR == MOV ENTONCES ACCION RENOVAR "
          "FECHA_TRAMITE 03/11/2026 CELULAR 989654321 "
          "OBSERVACION El cliente solicito renovar su servicio")


class TestLexico(unittest.TestCase):
    def test_clasifica_tokens(self):
        tokens, errores = lexico.analizar("SI TIPO_LINEA == PREPAGO 989654321 03/11/2026 hola")
        self.assertEqual([t.tipo for t in tokens],
                         ["RESERVADA", "VARIABLE", "OPERADOR_REL", "VALOR", "NUMERO", "FECHA", "TEXTO"])
        self.assertEqual(errores, [])

    def test_errores_lexicos_con_linea_y_columna(self):
        _, errores = lexico.analizar("SI X = Y\nCELULAR 12345 @")
        posiciones = [(e["linea"], e["columna"]) for e in errores]
        self.assertEqual(posiciones, [(1, 6), (2, 9), (2, 15)])


class TestAutomatas(unittest.TestCase):
    def test_afd_acepta_sus_lexemas(self):
        tokens, _ = lexico.analizar(VALIDA)
        for a in automatas.construir_automatas(tokens):
            for s in a["simulaciones"]:
                self.assertTrue(s["aceptada"], s["lexema"])

    def test_afd_minimo_equivale_al_de_subconjuntos(self):
        tokens, _ = lexico.analizar(VALIDA)
        rnd = random.Random(7)
        for a in automatas.construir_automatas(tokens):
            for _ in range(200):
                cad = "".join(rnd.choice("aZ_9/=0xSI") for _ in range(rnd.randint(0, 8)))
                self.assertEqual(automatas.simular(a["afd"], cad)[0],
                                 automatas.simular(a["afd_sub"], cad)[0], cad)

    def test_texto_se_minimiza_a_dos_estados(self):
        ast, _, _ = automatas.er_de_token("TEXTO", "hola")
        afd = automatas.minimizar(automatas.subconjuntos(automatas.thompson(ast)))
        self.assertEqual(len(afd.estados), 2)


class TestSintacticoYSemantico(unittest.TestCase):
    def test_cadena_valida_del_documento(self):
        r = compilar(VALIDA)
        self.assertTrue(r["aprobado"])
        self.assertIsNotNone(r["reglas"][0]["arbol_svg"])

    def test_orden_incorrecto(self):
        r = compilar("ENTONCES ACCION MIGRAR SI TIPO_LINEA == PREPAGO")
        self.assertFalse(r["aprobado"])
        self.assertIn("SI", r["errores"][0]["mensaje"])

    def test_falta_operador(self):
        r = compilar("SI TIPO_LINEA PREPAGO ENTONCES ACCION RENOVAR")
        self.assertIn("OPERADOR_REL", r["errores"][0]["mensaje"])

    def test_errores_semanticos(self):
        r = compilar("SI TIPO_LINEA == CLA Y OPERADOR > MOV ENTONCES ACCION MIGRAR "
                     "FECHA_TRAMITE 31/02/2026")
        self.assertEqual(len(r["errores"]), 3)
        self.assertTrue(all(e["fase"] == "Semántica" for e in r["errores"]))


class TestTraduccion(unittest.TestCase):
    def test_sql_y_json_solo_si_aprueba(self):
        ok = compilar(VALIDA)
        self.assertIn("INSERT INTO tramites_portabilidad", ok["sql"])
        self.assertIn('"accion": "RENOVAR"', ok["json"])
        mal = compilar("SI TIPO_LINEA PREPAGO ENTONCES ACCION RENOVAR")
        self.assertIsNone(mal["sql"])
        self.assertIsNone(mal["json"])

    def test_rendimiento_mas_de_1000_scripts_por_minuto(self):
        import time
        inicio = time.perf_counter()
        for _ in range(50):
            compilar(VALIDA)
        por_minuto = 50 / (time.perf_counter() - inicio) * 60
        self.assertGreater(por_minuto, 1000)


if __name__ == "__main__":
    unittest.main()
