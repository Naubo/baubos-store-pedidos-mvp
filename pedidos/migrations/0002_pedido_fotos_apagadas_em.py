from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pedidos", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="pedido",
            name="fotos_apagadas_em",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
