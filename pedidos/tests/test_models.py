from django.core.exceptions import ValidationError
from django.test import TestCase

from pedidos.models import Pedido, Produto, calcular_folhas


def criar_produto(**extra):
    dados = {
        "nome": "Kit de bottons",
        "formato": "botton",
        "largura_mm": 52,
        "altura_mm": 52,
        "fotos_por_kit": 6,
        "itens_por_folha": 12,
    }
    dados.update(extra)
    return Produto.objects.create(**dados)


def criar_pedido(produto=None, quantidade=1):
    return Pedido.objects.create(
        cliente_nome="Maria Souza",
        cliente_contato="maria@exemplo.com",
        produto=produto or criar_produto(),
        quantidade=quantidade,
        aceite_privacidade=True,
    )


class ProdutoTests(TestCase):
    def test_botton_de_52mm_cabe_12_por_folha(self):
        self.assertEqual(criar_produto().itens_por_folha_real, 12)

    def test_polaroid_de_75x55mm_usa_so_o_que_cabe_na_folha(self):
        # Com margem de 10 mm e espaço de 4 mm entre as peças, cabem 2 x 4 = 8.
        polaroid = criar_produto(nome="Kit de polaroids", formato="polaroid", largura_mm=75, altura_mm=55, itens_por_folha=11)
        self.assertEqual(polaroid.itens_por_folha_real, 8)

    def test_folhas_do_pedido_usam_a_capacidade_real(self):
        polaroid = criar_produto(nome="Kit de polaroids", formato="polaroid", largura_mm=75, altura_mm=55, fotos_por_kit=8, itens_por_folha=11)
        self.assertEqual(criar_pedido(polaroid, quantidade=2).folhas_necessarias, 2)

    def test_botton_precisa_ser_redondo(self):
        with self.assertRaises(ValidationError):
            Produto(nome="x", formato="botton", largura_mm=52, altura_mm=40, fotos_por_kit=1, itens_por_folha=12).clean()

    def test_peca_maior_que_a_folha_e_recusada(self):
        with self.assertRaises(ValidationError):
            Produto(nome="x", formato="polaroid", largura_mm=250, altura_mm=250, fotos_por_kit=1, itens_por_folha=1).clean()


class CalculoDeFolhasTests(TestCase):
    def test_arredonda_para_cima(self):
        self.assertEqual(calcular_folhas(24, 12), 2)
        self.assertEqual(calcular_folhas(25, 12), 3)
        self.assertEqual(calcular_folhas(1, 12), 1)


class PedidoModelTests(TestCase):
    def test_numero_do_pedido_e_gerado_automaticamente(self):
        pedido = criar_pedido()
        self.assertEqual(pedido.numero_pedido, f"BS-{pedido.pk:04d}")

    def test_total_de_fotos_e_folhas(self):
        pedido = criar_pedido(quantidade=3)  # 3 kits x 6 fotos = 18 peças
        self.assertEqual(pedido.total_fotos, 18)
        self.assertEqual(pedido.folhas_necessarias, 2)

    def test_status_comeca_em_recebido(self):
        self.assertEqual(criar_pedido().status, Pedido.STATUS_RECEBIDO)

    def test_status_avanca_uma_etapa_por_vez_na_ordem(self):
        pedido = criar_pedido()
        esperado = ["em_producao", "pronto", "enviado"]
        for status in esperado:
            pedido.avancar_status()
            pedido.refresh_from_db()
            self.assertEqual(pedido.status, status)

    def test_pedido_enviado_nao_avanca_mais(self):
        pedido = criar_pedido()
        for _ in range(3):
            pedido.avancar_status()
        self.assertIsNone(pedido.proximo_status)
        with self.assertRaises(ValueError):
            pedido.avancar_status()
