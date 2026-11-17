from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path("", views.novo_pedido, name="novo_pedido"),
    path("saude/", views.saude, name="saude"),
    path("pedido/enviado/", views.confirmacao, name="confirmacao"),
    path(
        "entrar/",
        auth_views.LoginView.as_view(authentication_form=LoginForm, redirect_authenticated_user=True),
        name="login",
    ),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    path("painel/", views.painel, name="painel"),
    path("painel/foto/<int:pk>/", views.foto, name="foto"),
    path("painel/<str:numero>/", views.detalhe_pedido, name="detalhe_pedido"),
    path("painel/<str:numero>/status/", views.avancar_status, name="avancar_status"),
    path("painel/<str:numero>/pdf/", views.baixar_pdf, name="baixar_pdf"),
]
