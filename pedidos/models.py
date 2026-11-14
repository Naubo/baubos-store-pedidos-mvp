import math

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Produto(models.Model):
    """Kit vendido pela loja (ex.: kit de polaroids, kit de bottons)."""

    FORMATO_POLAROID = "polaroid"
    FORMATO_BOTTON = "botton"
    FORMATOS = [
        (FORMATO_POLAROID, "Polaroid"),
        (FORMATO_BOTTON, "Botton"),
    ]

    nome = models.CharField(max_length=100, unique=True)
    formato = models.CharField(max_length=10, choices=FORMATOS)
    # Para botton, a largura é o diâmetro e a altura deve ser igual a ela.
    largura_mm = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    altura_mm = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    fotos_por_kit = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)]
    )
    itens_por_folha = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Pedido(models.Model):
    STATUS_RECEBIDO = "recebido"
    STATUS_EM_PRODUCAO = "em_producao"
    STATUS_PRONTO = "pronto"
    STATUS_ENVIADO = "enviado"
    STATUS = [
        (STATUS_RECEBIDO, "Recebido"),
        (STATUS_EM_PRODUCAO, "Em produção"),
        (STATUS_PRONTO, "Pronto"),
        (STATUS_ENVIADO, "Enviado"),
    ]
    # O status só anda para frente, uma etapa por vez, nesta ordem.
    ORDEM_STATUS = [s for s, _ in STATUS]

    numero_pedido = models.CharField(max_length=10, unique=True, null=True, blank=True, editable=False)
    cliente_nome = models.CharField(max_length=120)
    cliente_contato = models.CharField(max_length=120)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="pedidos")
    quantidade = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(60)]
    )
    observacoes = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS, default=STATUS_RECEBIDO)
    aceite_privacidade = models.BooleanField(default=False)
    pdf_arte = models.FileField(upload_to="pdfs/", null=True, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.numero_pedido or 'sem número'} - {self.cliente_nome}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.numero_pedido:
            self.numero_pedido = f"BS-{self.pk:04d}"
            super().save(update_fields=["numero_pedido"])

    @property
    def total_fotos(self):
        return self.produto.fotos_por_kit * self.quantidade

    @property
    def folhas_necessarias(self):
        return calcular_folhas(self.total_fotos, self.produto.itens_por_folha)

    @property
    def proximo_status(self):
        """Próxima etapa do pedido, ou None se já foi enviado."""
        posicao = self.ORDEM_STATUS.index(self.status)
        if posicao + 1 < len(self.ORDEM_STATUS):
            return self.ORDEM_STATUS[posicao + 1]
        return None

    def avancar_status(self):
        proximo = self.proximo_status
        if proximo is None:
            raise ValueError("O pedido já foi enviado e não tem próxima etapa.")
        self.status = proximo
        self.save(update_fields=["status", "atualizado_em"])


class Foto(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="fotos")
    arquivo = models.FileField(upload_to="fotos/")
    ordem = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["ordem"]
        constraints = [
            models.UniqueConstraint(fields=["pedido", "ordem"], name="foto_unica_por_ordem"),
        ]

    def __str__(self):
        return f"Foto {self.ordem} do pedido {self.pedido_id}"


def calcular_folhas(pecas, itens_por_folha):
    """Quantidade de folhas A4 para imprimir as peças (arredonda para cima)."""
    return math.ceil(pecas / itens_por_folha)
