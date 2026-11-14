"""Geração do PDF A4 com as fotos nas posições do layout e guias de corte."""
import io

from PIL import Image, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .layout import posicoes_na_folha

DPI = 300


def _mm_para_px(valor_mm):
    return round(valor_mm / 25.4 * DPI)


def gerar_pdf(imagens, formato, largura_mm, altura_mm, itens_por_folha, titulo):
    """Monta o PDF e devolve seus bytes.

    `imagens` é uma lista de bytes de imagens já tratadas. Cada foto é cortada
    (centralizada) na proporção exata da peça, então não sobra borda nem distorce.
    """
    posicoes = posicoes_na_folha(largura_mm, altura_mm, itens_por_folha)
    por_folha = len(posicoes)
    total_folhas = -(-len(imagens) // por_folha)  # divisão arredondada para cima

    saida = io.BytesIO()
    pdf = canvas.Canvas(saida, pagesize=A4)
    pdf.setTitle(titulo)

    for numero_folha in range(total_folhas):
        grupo = imagens[numero_folha * por_folha : (numero_folha + 1) * por_folha]
        for dados, (x, y) in zip(grupo, posicoes):
            with Image.open(io.BytesIO(dados)) as original:
                ajustada = ImageOps.fit(
                    original.convert("RGB"),
                    (_mm_para_px(largura_mm), _mm_para_px(altura_mm)),
                    Image.LANCZOS,
                )
            pdf.drawImage(ImageReader(ajustada), x * mm, y * mm, largura_mm * mm, altura_mm * mm)

            # Guia de corte: círculo para botton, retângulo para polaroid.
            pdf.setStrokeColorRGB(0.4, 0.4, 0.4)
            pdf.setLineWidth(0.3)
            if formato == "botton":
                raio = min(largura_mm, altura_mm) / 2
                pdf.circle((x + largura_mm / 2) * mm, (y + altura_mm / 2) * mm, raio * mm)
            else:
                pdf.rect(x * mm, y * mm, largura_mm * mm, altura_mm * mm)

        pdf.setFont("Helvetica", 7)
        pdf.setFillColorRGB(0.3, 0.3, 0.3)
        pdf.drawString(10 * mm, 5 * mm, f"{titulo} - folha {numero_folha + 1} de {total_folhas}")
        pdf.showPage()

    pdf.save()
    return saida.getvalue()
