from django.shortcuts import redirect, render

from .forms import PedidoForm
from .models import Produto


def novo_pedido(request):
    """Tela 1: formulário do cliente (público)."""
    if request.method == "POST":
        form = PedidoForm(request.POST, request.FILES)
        if form.is_valid():
            pedido = form.salvar()
            request.session["ultimo_pedido"] = pedido.numero_pedido
            return redirect("confirmacao")
    else:
        form = PedidoForm()
    kits = Produto.objects.filter(ativo=True)
    return render(request, "pedidos/novo_pedido.html", {"form": form, "kits": kits})


def confirmacao(request):
    """Tela 3: confirmação. Só mostra o número do pedido recém-enviado."""
    numero = request.session.get("ultimo_pedido")
    if not numero:
        return redirect("novo_pedido")
    return render(request, "pedidos/confirmacao.html", {"numero": numero})
