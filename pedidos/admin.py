from django.contrib import admin

from .models import Pedido, Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """RF01: cadastro, edição e desativação de kits."""

    list_display = ("nome", "formato", "largura_mm", "altura_mm", "fotos_por_kit", "itens_por_folha", "ativo")
    list_filter = ("formato", "ativo")
    search_fields = ("nome",)

    def has_delete_permission(self, request, obj=None):
        # Kit que já tem pedidos só pode ser desativado, nunca apagado.
        if obj is not None and obj.pedidos.exists():
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("numero_pedido", "cliente_nome", "produto", "status", "criado_em")
    list_filter = ("status",)
    readonly_fields = ("numero_pedido", "criado_em", "atualizado_em")
