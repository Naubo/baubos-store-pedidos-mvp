from django.urls import path

from . import views

urlpatterns = [
    path("", views.novo_pedido, name="novo_pedido"),
    path("pedido/enviado/", views.confirmacao, name="confirmacao"),
]
