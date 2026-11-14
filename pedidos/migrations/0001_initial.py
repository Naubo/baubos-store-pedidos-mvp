import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Produto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nome", models.CharField(max_length=100, unique=True)),
                ("formato", models.CharField(choices=[("polaroid", "Polaroid"), ("botton", "Botton")], max_length=10)),
                ("largura_mm", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("altura_mm", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                (
                    "fotos_por_kit",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(60),
                        ]
                    ),
                ),
                ("itens_por_folha", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ("ativo", models.BooleanField(default=True)),
            ],
            options={"ordering": ["nome"]},
        ),
        migrations.CreateModel(
            name="Pedido",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero_pedido", models.CharField(blank=True, editable=False, max_length=10, null=True, unique=True)),
                ("cliente_nome", models.CharField(max_length=120)),
                ("cliente_contato", models.CharField(max_length=120)),
                (
                    "quantidade",
                    models.PositiveSmallIntegerField(
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(60),
                        ]
                    ),
                ),
                ("observacoes", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("recebido", "Recebido"),
                            ("em_producao", "Em produção"),
                            ("pronto", "Pronto"),
                            ("enviado", "Enviado"),
                        ],
                        default="recebido",
                        max_length=15,
                    ),
                ),
                ("aceite_privacidade", models.BooleanField(default=False)),
                ("pdf_arte", models.FileField(blank=True, null=True, upload_to="pdfs/")),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                (
                    "produto",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="pedidos",
                        to="pedidos.produto",
                    ),
                ),
            ],
            options={"ordering": ["-criado_em"]},
        ),
        migrations.CreateModel(
            name="Foto",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("arquivo", models.FileField(upload_to="fotos/")),
                ("ordem", models.PositiveSmallIntegerField()),
                (
                    "pedido",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fotos",
                        to="pedidos.pedido",
                    ),
                ),
            ],
            options={"ordering": ["ordem"]},
        ),
        migrations.AddConstraint(
            model_name="foto",
            constraint=models.UniqueConstraint(fields=("pedido", "ordem"), name="foto_unica_por_ordem"),
        ),
    ]
