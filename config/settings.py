"""Configurações do projeto Baubos Store: Pedidos.

Segredos e opções sensíveis vêm de variáveis de ambiente (nunca do código):
DJANGO_SECRET_KEY, DJANGO_DEBUG e DJANGO_ALLOWED_HOSTS.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get("DJANGO_DEBUG", "0") == "1"

# Em produção a chave é obrigatória. Só em modo DEBUG (desenvolvimento local)
# existe uma chave temporária, para o projeto rodar sem configuração extra.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "chave-apenas-para-desenvolvimento-local"
    else:
        from django.core.exceptions import ImproperlyConfigured

        raise ImproperlyConfigured("Defina a variável de ambiente DJANGO_SECRET_KEY.")

ALLOWED_HOSTS = [h for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if h]
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "pedidos",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Senhas: PBKDF2-SHA256 (padrão do Django) com mínimo de 12 caracteres.
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Fotos e PDFs ficam fora de qualquer URL pública: só saem por views com login.
MEDIA_ROOT = BASE_DIR / "uploads"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login e sessão
LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "painel"
LOGOUT_REDIRECT_URL = "login"
SESSION_COOKIE_AGE = 8 * 60 * 60  # 8 horas
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = False  # o PythonAnywhere já entrega tudo em HTTPS

# Bloqueio de login: 5 falhas em 15 minutos
LOGIN_MAX_FALHAS = 5
LOGIN_JANELA_SEGUNDOS = 15 * 60

# Regras de negócio do pedido
MAX_FOTOS_POR_PEDIDO = 60
MAX_TAMANHO_FOTO_BYTES = 15 * 1024 * 1024  # 15 MB
LADO_MAIOR_FOTO_PX = 2000
