"""Tratamento das fotos enviadas pelo cliente.

Regras: só JPG ou PNG verificados pelo conteúdo (não pela extensão), até 15 MB.
A foto é reduzida (lado maior de 2000 px) e só a versão reduzida é guardada.
Este módulo não depende do Django, então dá para testar de forma isolada.
"""
import io

from PIL import Image, ImageOps, UnidentifiedImageError

FORMATOS_ACEITOS = {"JPEG", "PNG"}
# Protege o servidor contra imagens "bomba" (poucos KB que viram bilhões de pixels).
Image.MAX_IMAGE_PIXELS = 60_000_000


class FotoInvalida(Exception):
    """A foto enviada não pode ser aceita. A mensagem é exibida ao cliente."""


def processar_foto(arquivo, max_bytes, lado_maior_px):
    """Valida e reduz a foto. Devolve os bytes de um JPEG novo.

    `arquivo` é qualquer objeto com `.read()` (ex.: UploadedFile do Django).
    """
    dados = arquivo.read(max_bytes + 1)
    if len(dados) > max_bytes:
        limite_mb = max_bytes // (1024 * 1024)
        raise FotoInvalida(f"A foto é maior que {limite_mb} MB.")
    if not dados:
        raise FotoInvalida("O arquivo está vazio.")

    try:
        # verify() só checa a integridade; depois é preciso abrir de novo para usar.
        Image.open(io.BytesIO(dados)).verify()
        imagem = Image.open(io.BytesIO(dados))
        formato = imagem.format
        if formato not in FORMATOS_ACEITOS:
            raise FotoInvalida("Envie apenas fotos em JPG ou PNG.")
        imagem.load()
    except FotoInvalida:
        raise
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, SyntaxError, ValueError):
        raise FotoInvalida("Não foi possível ler este arquivo como foto JPG ou PNG.")

    imagem = ImageOps.exif_transpose(imagem)  # respeita a rotação do celular
    if imagem.mode in ("RGBA", "LA", "P"):
        fundo = Image.new("RGB", imagem.size, (255, 255, 255))
        imagem = imagem.convert("RGBA")
        fundo.paste(imagem, mask=imagem.split()[-1])
        imagem = fundo
    else:
        imagem = imagem.convert("RGB")

    imagem.thumbnail((lado_maior_px, lado_maior_px))
    saida = io.BytesIO()
    imagem.save(saida, format="JPEG", quality=90)
    return saida.getvalue()
