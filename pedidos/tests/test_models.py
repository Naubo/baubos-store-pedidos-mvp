from django.test import TestCase

from pedidos.models import Pedido, Produto, calcular_folhas


def criar_produto(**extra):
    dados = {
        "nome": "Kit de bottons",
        "formato": "botton",
        "largura_mm": 58,
        "altura_mm": 58,
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
