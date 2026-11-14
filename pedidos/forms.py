import uuid

from django import forms
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import transaction

from .arte.fotos import FotoInvalida, processar_foto
from .arte.pdf import gerar_pdf
from .models import Foto, Pedido, Produto


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """Campo que aceita várias fotos de uma vez (padrão da documentação do Django)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        limpar = super().clean
        if isinstance(data, (list, tuple)):
            return [limpar(item, initial) for item in data]
        return [limpar(data, initial)]


class PedidoForm(forms.Form):
    """Formulário público (RF02): o cliente escolhe o kit e envia as fotos."""

    cliente_nome = forms.CharField(label="Seu nome", max_length=120)
    cliente_contato = forms.CharField(label="WhatsApp ou e-mail para contato", max_length=120)
    produto = forms.ModelChoiceField(
        label="Kit",
        queryset=Produto.objects.filter(ativo=True),
        empty_label="Escolha o kit",
    )
    quantidade = forms.IntegerField(
        label="Quantidade de kits",
        min_value=1,
        max_value=settings.MAX_FOTOS_POR_PEDIDO,
        initial=1,
    )
    fotos = MultipleFileField(
        label="Fotos (JPG ou PNG, até 15 MB cada)",
        help_text="Envie todas as fotos de uma vez. O total deve ser igual ao número de fotos do kit vezes a quantidade.",
    )
    observacoes = forms.CharField(label="Observações", required=False, widget=forms.Textarea(attrs={"rows": 3}))
    aceite_privacidade = forms.BooleanField(
        label="Autorizo a Baubos Store a usar minhas fotos somente para produzir este pedido. "
        "Elas serão apagadas depois do envio.",
        error_messages={"required": "Para continuar, é preciso autorizar o uso das fotos."},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fotos_processadas = []
        self.fields["fotos"].widget.attrs.update({"accept": "image/jpeg,image/png"})

    def clean(self):
        dados = super().clean()
        produto = dados.get("produto")
        quantidade = dados.get("quantidade")
        fotos = dados.get("fotos")
        if not (produto and quantidade and fotos):
            return dados

        total = produto.fotos_por_kit * quantidade
        if total > settings.MAX_FOTOS_POR_PEDIDO:
            self.add_error(
                "quantidade",
                f"Esse pedido teria {total} fotos e o máximo é {settings.MAX_FOTOS_POR_PEDIDO}. Diminua a quantidade.",
            )
            return dados
        if len(fotos) != total:
            self.add_error(
                "fotos",
                f"Você enviou {len(fotos)} foto(s), mas {quantidade} kit(s) de {produto.nome} precisam de {total}.",
            )
            return dados

        processadas = []
        for numero, arquivo in enumerate(fotos, start=1):
            try:
                processadas.append(
                    processar_foto(arquivo, settings.MAX_TAMANHO_FOTO_BYTES, settings.LADO_MAIOR_FOTO_PX)
                )
            except FotoInvalida as erro:
                self.add_error("fotos", f"Foto {numero} ({arquivo.name}): {erro}")
        if not self.errors:
            self.fotos_processadas = processadas
        return dados

    @transaction.atomic
    def salvar(self):
        """Cria o pedido, guarda as fotos reduzidas e gera o PDF de impressão."""
        dados = self.cleaned_data
        produto = dados["produto"]
        pedido = Pedido.objects.create(
            cliente_nome=dados["cliente_nome"],
            cliente_contato=dados["cliente_contato"],
            produto=produto,
            quantidade=dados["quantidade"],
            observacoes=dados["observacoes"],
            aceite_privacidade=True,
        )
        for ordem, conteudo in enumerate(self.fotos_processadas, start=1):
            foto = Foto(pedido=pedido, ordem=ordem)
            # O nome do arquivo é gerado pelo sistema, nunca o enviado pelo cliente.
            foto.arquivo.save(f"{uuid.uuid4().hex}.jpg", ContentFile(conteudo), save=False)
            foto.save()

        pdf = gerar_pdf(
            self.fotos_processadas,
            produto.formato,
            produto.largura_mm,
            produto.altura_mm,
            produto.itens_por_folha,
            pedido.numero_pedido,
        )
        pedido.pdf_arte.save(f"{pedido.numero_pedido}-{uuid.uuid4().hex[:8]}.pdf", ContentFile(pdf), save=False)
        pedido.save(update_fields=["pdf_arte", "atualizado_em"])
        return pedido
