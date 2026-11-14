from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    # O login do admin passa pelo mesmo login do painel, que tem bloqueio por tentativas.
    path("admin/login/", RedirectView.as_view(pattern_name="login", query_string=True)),
    path("admin/", admin.site.urls),
    path("", include("pedidos.urls")),
]
