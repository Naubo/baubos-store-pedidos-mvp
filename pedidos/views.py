from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PedidoForm
from .models import Foto, Pedido, Produto


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


# ---------- Painel do responsável (todas as telas exigem login) ----------


@login_required
def painel(request):
    """Tela 2: lista dos pedidos com filtro por status (RF04)."""
    status = request.GET.get("status", "")
    pedidos = Pedido.objects.select_related("produto")
    if status in Pedido.ORDEM_STATUS:
        pedidos = pedidos.filter(status=status)
    else:
        status = ""
    contexto = {"pedidos": pedidos[:50], "status_atual": status, "opcoes_status": Pedido.STATUS}
    return render(request, "pedidos/painel.html", contexto)


@login_required
def detalhe_pedido(request, numero):
    pedido = get_object_or_404(Pedido.objects.select_related("produto"), numero_pedido=numero)
    return render(request, "pedidos/detalhe_pedido.html", {"pedido": pedido, "fotos": pedido.fotos.all()})


@login_required
@require_POST
def avancar_status(request, numero):
    """RF05: avança uma etapa por vez, sem voltar."""
    pedido = get_object_or_404(Pedido, numero_pedido=numero)
    try:
        pedido.avancar_status()
    except ValueError as erro:
        messages.error(request, str(erro))
    else:
        messages.success(request, f"Pedido {pedido.numero_pedido} agora está: {pedido.get_status_display()}.")
    return redirect("detalhe_pedido", numero=numero)


@login_required
def foto(request, pk):
    """Entrega a foto só para quem está logado (não existe URL pública de mídia)."""
    registro = get_object_or_404(Foto, pk=pk)
    return FileResponse(registro.arquivo.open("rb"), content_type="image/jpeg")


@login_required
def baixar_pdf(request, numero):
    pedido = get_object_or_404(Pedido, numero_pedido=numero)
    if not pedido.pdf_arte:
        raise Http404("Este pedido não tem PDF.")
    return FileResponse(
        pedido.pdf_arte.open("rb"),
        as_attachment=True,
        filename=f"{pedido.numero_pedido}.pdf",
        content_type="application/pdf",
    )
