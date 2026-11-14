"""Bloqueio de login: depois de 5 falhas em 15 minutos, o usuário fica bloqueado."""
from django.conf import settings
from django.core.cache import cache


def _chave(usuario):
    return f"login-falhas:{usuario.strip().lower()}"


def esta_bloqueado(usuario):
    return cache.get(_chave(usuario), 0) >= settings.LOGIN_MAX_FALHAS


def registrar_falha(usuario):
    chave = _chave(usuario)
    if cache.add(chave, 1, settings.LOGIN_JANELA_SEGUNDOS):
        return 1
    try:
        return cache.incr(chave)
    except ValueError:  # a chave expirou entre o add e o incr
        cache.set(chave, 1, settings.LOGIN_JANELA_SEGUNDOS)
        return 1


def limpar_falhas(usuario):
    cache.delete(_chave(usuario))
