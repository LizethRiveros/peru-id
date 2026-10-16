import unittest

from peru_id import (digito_ruc, generar_ruc_prueba, validar_cci, validar_dni, validar_ruc, validar_telefono)


class Ruc(unittest.TestCase):
    def test_rucs_reales_conocidos(self):
        # RUC de empresas publicas del Padron Reducido SUNAT
        for r in ("20522088073", "20100099447", "20100162076"):
            self.assertTrue(validar_ruc(r)["valido"], r)

    def test_errores(self):
        self.assertFalse(validar_ruc("20522088074")["valido"])      # digito verificador mal
        self.assertFalse(validar_ruc("2052208807")["valido"])       # 10 digitos
        self.assertFalse(validar_ruc("30522088073")["valido"])      # prefijo inexistente
        self.assertFalse(validar_ruc("")["valido"])
        self.assertFalse(validar_ruc("abcdefghijk")["valido"])
        self.assertIn("deberia ser 3", validar_ruc("20522088074")["motivo"])

    def test_tolera_espacios_y_guiones(self):
        self.assertTrue(validar_ruc("20 5220 88073")["valido"])
        self.assertTrue(validar_ruc("20522088073 ")["valido"])

    def test_generador(self):
        rucs = generar_ruc_prueba(200, semilla=1)
        self.assertEqual(len(set(rucs)), len(rucs))
        for r in rucs:
            self.assertTrue(r.startswith("2099"))
            self.assertTrue(validar_ruc(r)["valido"])
        self.assertEqual(generar_ruc_prueba(3, semilla=5), generar_ruc_prueba(3, semilla=5))

    def test_digito_resultados_10_y_11(self):
        # el resto 10 -> 0 y el resto 11 -> 1 (11 - (suma % 11) = 10 u 11)
        for base in (f"20{n:08d}" for n in range(100)):
            d = digito_ruc(base)
            self.assertIn(d, range(10))


class Dni(unittest.TestCase):
    def test_formato(self):
        self.assertTrue(validar_dni("12345678")["valido"])
        self.assertFalse(validar_dni("1234567")["valido"])
        self.assertFalse(validar_dni("1234567a")["valido"])


class Cci(unittest.TestCase):
    def test_estructura_y_banco_verificado(self):
        r = validar_cci("018-123-123456789012-34")
        self.assertTrue(r["valido"])
        self.assertEqual(r["entidad"]["nombre"], "Banco de la Nacion")
        self.assertTrue(r["entidad"]["verificado"])
        self.assertEqual((r["oficina"], r["cuenta"], r["digitos_control"]), ("123", "123456789012", "34"))

    def test_banco_no_verificado_avisa(self):
        r = validar_cci("00212345678901234567")
        self.assertFalse(r["entidad"]["verificado"])
        self.assertIn("aviso", r)

    def test_banco_desconocido_no_es_invalido(self):
        r = validar_cci("99912345678901234567")
        self.assertTrue(r["valido"])
        self.assertIsNone(r["entidad"]["nombre"])

    def test_longitud(self):
        self.assertFalse(validar_cci("0181234567890123456")["valido"])
        self.assertFalse(validar_cci("018123456789012345678")["valido"])


class Telefono(unittest.TestCase):
    def test_formatos(self):
        self.assertEqual(validar_telefono("987 654 321")["tipo"], "movil")
        self.assertEqual(validar_telefono("+51 987654321")["internacional"], "+51987654321")
        self.assertEqual(validar_telefono("51987654321")["tipo"], "movil")
        self.assertEqual(validar_telefono("(01) 234-5678")["tipo"], "fijo Lima")
        self.assertEqual(validar_telefono("064 212345")["tipo"], "fijo provincia")

    def test_prefijo_puno_no_se_confunde_con_codigo_de_pais(self):
        r = validar_telefono("51 123456")        # Puno: prefijo 51 + 6 digitos
        self.assertTrue(r["valido"])
        self.assertEqual(r["tipo"], "fijo provincia")

    def test_invalidos(self):
        for t in ("12345", "887654321", "", "abc"):
            self.assertFalse(validar_telefono(t)["valido"], t)


if __name__ == "__main__":
    unittest.main()
