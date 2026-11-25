from rest_framework.permissions import SAFE_METHODS, BasePermission


class PermissaoPorPapel(BasePermission):
    """Leitura para qualquer perfil; escrita só para admin.

    A view libera ações para o operador com o atributo `operador_pode`.
    """

    message = 'Seu papel não permite esta ação.'

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated or not hasattr(user, 'perfil'):
            return False
        if request.method in SAFE_METHODS or user.perfil.eh_admin:
            return True
        return getattr(view, 'action', None) in getattr(view, 'operador_pode', ())
