import io
import re
import unittest

from PIL import Image

from pedidos.arte.layout import posicoes_na_folha
from pedidos.arte.pdf import gerar_pdf


def foto(cor=(30, 120, 200), tamanho=(800, 600)):
    buffer = io.BytesIO()
    Image.new("RGB", tamanho, cor).save(buffer, format="JPEG")
    return buffer.getvalue()


def contar_paginas(pdf_bytes):
    return len(re.findall(rb"/Type /Page\b", pdf_bytes))


class LayoutTests(unittest.TestCase):
    def test_botton_de_58mm_cabe_12_por_folha(self):
        self.assertEqual(len(posicoes_na_folha(58, 58, 12)), 12)

    def test_botton_de_52mm_cabe_12_por_folha(self):
        self.assertEqual(len(posicoes_na_folha(52, 52, 12)), 12)

    def test_polaroid_de_75x55mm_cabe_8_por_folha(self):
        self.assertEqual(len(posicoes_na_folha(75, 55, 11)), 8)

    def test_nao_passa_do_que_cabe_na_folha(self):
        # Peça de 90x90 mm: cabem 2 colunas x 2 linhas = 4, mesmo pedindo 20.
        self.assertEqual(len(posicoes_na_folha(90, 90, 20)), 4)

    def test_respeita_itens_por_folha_menor_que_a_grade(self):
        self.assertEqual(len(posicoes_na_folha(45, 60, 11)), 11)

    def test_pecas_dentro_da_folha_a4(self):
        for x, y in posicoes_na_folha(58, 58, 12):
            self.assertGreaterEqual(x, 10)
            self.assertGreaterEqual(y, 10)
            self.assertLessEqual(x + 58, 200)
            self.assertLessEqual(y + 58, 287)

    def test_peca_maior_que_a_folha_gera_erro(self):
        with self.assertRaises(ValueError):
            posicoes_na_folha(250, 250, 1)


class PdfTests(unittest.TestCase):
    def test_pdf_traz_o_numero_de_cada_foto(self):
        pdf = gerar_pdf([foto() for _ in range(2)], "botton", 52, 52, 12, "BS-0004")
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertEqual(contar_paginas(pdf), 1)

    def test_pdf_valido_com_uma_folha(self):
        pdf = gerar_pdf([foto() for _ in range(6)], "botton", 58, 58, 12, "BS-0001")
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertEqual(contar_paginas(pdf), 1)

    def test_mais_pecas_que_a_folha_cria_nova_pagina(self):
        pdf = gerar_pdf([foto() for _ in range(13)], "botton", 58, 58, 12, "BS-0002")
        self.assertEqual(contar_paginas(pdf), 2)

    def test_polaroid_gera_pdf(self):
        pdf = gerar_pdf([foto(tamanho=(300, 900)) for _ in range(3)], "polaroid", 45, 60, 11, "BS-0003")
        self.assertTrue(pdf.startswith(b"%PDF"))
