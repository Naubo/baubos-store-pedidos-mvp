import io
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from pedidos.models import Foto, Pedido

from .test_models import criar_produto

MEDIA_TESTE = tempfile.mkdtemp()
SENHA = "senha-segura-123"


def foto_upload(nome="foto.jpg", formato="JPEG", tamanho=(600, 400)):
    buffer = io.BytesIO()
    Image.new("RGB", tamanho, (10, 120, 200)).save(buffer, format=formato)
    tipo = "image/jpeg" if formato == "JPEG" else "image/png"
    return SimpleUploadedFile(nome, buffer.getvalue(), content_type=tipo)


@override_settings(MEDIA_ROOT=MEDIA_TESTE)
class BaseIntegracao(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TESTE, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.produto = criar_produto(fotos_por_kit=2, itens_por_folha=12)

    def dados_pedido(self, fotos=None, **extra):
        dados = {
            "cliente_nome": "Maria Souza",
            "cliente_contato": "maria@exemplo.com",
            "produto": self.produto.pk,
            "quantidade": 1,
            "aceite_privacidade": "on",
            "fotos": fotos if fotos is not None else [foto_upload("a.jpg"), foto_upload("b.png", "PNG")],
        }
        dados.update(extra)
        return dados

    def enviar_pedido(self, **kwargs):
        return self.client.post(reverse("novo_pedido"), self.dados_pedido(**kwargs))


class FormularioPublicoTests(BaseIntegracao):
    def test_formulario_abre_sem_login(self):
        resposta = self.client.get(reverse("novo_pedido"))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Faça seu pedido")

    def test_pedido_valido_cria_pedido_fotos_e_pdf(self):
        resposta = self.enviar_pedido()
        self.assertRedirects(resposta, reverse("confirmacao"))
        pedido = Pedido.objects.get()
        self.assertEqual(pedido.fotos.count(), 2)
        self.assertTrue(pedido.pdf_arte.name.endswith(".pdf"))
        confirmacao = self.client.get(reverse("confirmacao"))
        self.assertContains(confirmacao, pedido.numero_pedido)

    def test_nome_do_arquivo_e_gerado_pelo_sistema(self):
        fotos = [foto_upload("../../etc/passwd.jpg"), foto_upload("minha foto.jpg")]
        self.enviar_pedido(fotos=fotos)
        for foto in Foto.objects.all():
            self.assertRegex(foto.arquivo.name, r"^fotos/[0-9a-f]{32}\.jpg$")

    def test_quantidade_de_fotos_diferente_do_kit_e_recusada(self):
        resposta = self.enviar_pedido(fotos=[foto_upload()])
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "precisam de 2")
        self.assertEqual(Pedido.objects.count(), 0)

    def test_pedido_sem_nenhuma_foto_e_recusado(self):
        resposta = self.enviar_pedido(fotos=[])
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_arquivo_que_nao_e_foto_e_recusado(self):
        falso = SimpleUploadedFile("virus.jpg", b"isto nao e uma imagem", content_type="image/jpeg")
        resposta = self.enviar_pedido(fotos=[falso, foto_upload()])
        self.assertContains(resposta, "Não foi possível ler")
        self.assertEqual(Pedido.objects.count(), 0)

    def test_sem_aceite_de_privacidade_e_recusado(self):
        dados = self.dados_pedido()
        del dados["aceite_privacidade"]
        resposta = self.client.post(reverse("novo_pedido"), dados)
        self.assertContains(resposta, "autorizar o uso das fotos")
        self.assertEqual(Pedido.objects.count(), 0)

    def test_pedido_acima_de_60_fotos_e_recusado(self):
        self.produto.fotos_por_kit = 40
        self.produto.save()
        resposta = self.enviar_pedido(quantidade=2)
        self.assertContains(resposta, "máximo é 60")
        self.assertEqual(Pedido.objects.count(), 0)

    def test_kit_desativado_nao_pode_ser_escolhido(self):
        self.produto.ativo = False
        self.produto.save()
        resposta = self.enviar_pedido()
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_confirmacao_sem_pedido_volta_para_o_formulario(self):
        self.assertRedirects(self.client.get(reverse("confirmacao")), reverse("novo_pedido"))


class PainelTests(BaseIntegracao):
    def setUp(self):
        super().setUp()
        self.enviar_pedido()
        self.pedido = Pedido.objects.get()
        get_user_model().objects.create_user("dona", password=SENHA)

    def entrar(self):
        self.assertTrue(self.client.login(username="dona", password=SENHA))

    def test_visitante_e_enviado_para_o_login(self):
        self.client.logout()
        urls = [
            reverse("painel"),
            reverse("detalhe_pedido", args=[self.pedido.numero_pedido]),
            reverse("baixar_pdf", args=[self.pedido.numero_pedido]),
            reverse("foto", args=[self.pedido.fotos.first().pk]),
        ]
        for url in urls:
            resposta = self.client.get(url)
            self.assertEqual(resposta.status_code, 302, url)
            self.assertTrue(resposta["Location"].startswith(reverse("login")), url)

    def test_visitante_nao_consegue_avancar_status(self):
        self.client.logout()
        self.client.post(reverse("avancar_status", args=[self.pedido.numero_pedido]))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, Pedido.STATUS_RECEBIDO)

    def test_lista_mostra_o_pedido_e_filtra_por_status(self):
        self.entrar()
        self.assertContains(self.client.get(reverse("painel")), self.pedido.numero_pedido)
        self.assertContains(self.client.get(reverse("painel"), {"status": "recebido"}), self.pedido.numero_pedido)
        self.assertNotContains(self.client.get(reverse("painel"), {"status": "pronto"}), self.pedido.numero_pedido)

    def test_avancar_status_por_post(self):
        self.entrar()
        self.client.post(reverse("avancar_status", args=[self.pedido.numero_pedido]))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, Pedido.STATUS_EM_PRODUCAO)

    def test_avancar_status_por_get_nao_e_permitido(self):
        self.entrar()
        resposta = self.client.get(reverse("avancar_status", args=[self.pedido.numero_pedido]))
        self.assertEqual(resposta.status_code, 405)

    def test_download_do_pdf(self):
        self.entrar()
        resposta = self.client.get(reverse("baixar_pdf", args=[self.pedido.numero_pedido]))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta["Content-Type"], "application/pdf")
        conteudo = b"".join(resposta.streaming_content)
        self.assertTrue(conteudo.startswith(b"%PDF"))

    def test_foto_e_entregue_para_quem_esta_logado(self):
        self.entrar()
        resposta = self.client.get(reverse("foto", args=[self.pedido.fotos.first().pk]))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta["Content-Type"], "image/jpeg")
        b"".join(resposta.streaming_content)

    def test_pedido_inexistente_da_404(self):
        self.entrar()
        self.assertEqual(self.client.get(reverse("detalhe_pedido", args=["BS-9999"])).status_code, 404)


class LoginTests(BaseIntegracao):
    def setUp(self):
        super().setUp()
        get_user_model().objects.create_user("dona", password=SENHA)

    def test_login_correto_leva_ao_painel(self):
        resposta = self.client.post(reverse("login"), {"username": "dona", "password": SENHA})
        self.assertRedirects(resposta, reverse("painel"), fetch_redirect_response=False)

    def test_mensagem_de_erro_e_a_mesma_para_usuario_ou_senha_errados(self):
        senha_errada = self.client.post(reverse("login"), {"username": "dona", "password": "errada"})
        usuario_errado = self.client.post(reverse("login"), {"username": "outra", "password": "errada"})
        for resposta in (senha_errada, usuario_errado):
            self.assertContains(resposta, "Usuário ou senha incorretos.")

    def test_bloqueio_depois_de_5_falhas(self):
        for _ in range(5):
            self.client.post(reverse("login"), {"username": "dona", "password": "errada"})
        resposta = self.client.post(reverse("login"), {"username": "dona", "password": SENHA})
        self.assertContains(resposta, "Muitas tentativas")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_do_admin_usa_o_login_com_bloqueio(self):
        resposta = self.client.get("/admin/login/")
        self.assertEqual(resposta.status_code, 302)
        self.assertTrue(resposta["Location"].startswith(reverse("login")))

    def test_senha_curta_e_recusada_pelo_validador(self):
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            validate_password("curta123")
