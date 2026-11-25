"""Quem está logado, de qual organização é e o que pode fazer."""
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render


def org_atual(request):
    # A organização vem SEMPRE do usuário logado, nunca da URL ou do formulário.
    return request.user.perfil.organizacao


def perfil_requerido(view):
    """Exige login e perfil (um superusuário sem perfil é barrado com aviso)."""
    @login_required
    @wraps(view)
    def interna(request, *args, **kwargs):
        if not hasattr(request.user, 'perfil'):
            return render(request, 'core/sem_perfil.html', status=403)
        return view(request, *args, **kwargs)
    return interna


def papel_requerido(*papeis):
    """Exige que o perfil tenha um dos papéis; senão, 403."""
    def decorador(view):
        @perfil_requerido
        @wraps(view)
        def interna(request, *args, **kwargs):
            if request.user.perfil.papel not in papeis:
                raise PermissionDenied
            return view(request, *args, **kwargs)
        return interna
    return decorador
