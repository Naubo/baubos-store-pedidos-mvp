import io
import unittest

from PIL import Image

from pedidos.arte.fotos import FotoInvalida, processar_foto

LIMITE = 15 * 1024 * 1024


def gerar_imagem(formato, tamanho=(3000, 1500), modo="RGB"):
    buffer = io.BytesIO()
    Image.new(modo, tamanho, (200, 10, 10)).save(buffer, format=formato)
    buffer.seek(0)
    return buffer


class ProcessarFotoTests(unittest.TestCase):
    def test_png_grande_e_reduzido_para_2000px_e_vira_jpeg(self):
        resultado = processar_foto(gerar_imagem("PNG"), LIMITE, 2000)
        imagem = Image.open(io.BytesIO(resultado))
        self.assertEqual(imagem.format, "JPEG")
        self.assertEqual(max(imagem.size), 2000)

    def test_foto_pequena_nao_e_ampliada(self):
        resultado = processar_foto(gerar_imagem("JPEG", (400, 300)), LIMITE, 2000)
        self.assertEqual(Image.open(io.BytesIO(resultado)).size, (400, 300))

    def test_png_com_transparencia_e_aceito(self):
        resultado = processar_foto(gerar_imagem("PNG", (50, 50), "RGBA"), LIMITE, 2000)
        self.assertEqual(Image.open(io.BytesIO(resultado)).mode, "RGB")

    def test_arquivo_que_nao_e_imagem_e_recusado(self):
        with self.assertRaises(FotoInvalida):
            processar_foto(io.BytesIO(b"isto nao e uma foto"), LIMITE, 2000)

    def test_formato_diferente_de_jpg_png_e_recusado_pelo_conteudo(self):
        with self.assertRaises(FotoInvalida):
            processar_foto(gerar_imagem("GIF", (10, 10), "P"), LIMITE, 2000)

    def test_arquivo_vazio_e_recusado(self):
        with self.assertRaises(FotoInvalida):
            processar_foto(io.BytesIO(b""), LIMITE, 2000)

    def test_arquivo_acima_do_limite_e_recusado(self):
        with self.assertRaises(FotoInvalida):
            processar_foto(io.BytesIO(b"x" * 101), 100, 2000)
