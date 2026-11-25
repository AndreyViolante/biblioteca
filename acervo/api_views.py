from django.db.models import ProtectedError
from rest_framework import status, viewsets
from rest_framework.response import Response

from core.acesso import org_atual

from .models import Autor, Categoria, Livro
from .serializers import AutorSerializer, CategoriaSerializer, LivroSerializer


class DaOrganizacaoMixin:
    """Isolamento da API: lista, cria e apaga só dentro da organização."""

    def get_queryset(self):
        return super().get_queryset().filter(organizacao=org_atual(self.request))

    def perform_create(self, serializer):
        serializer.save(organizacao=org_atual(self.request))

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({'detail': 'Registro em uso, não pode ser excluído.'},
                            status=status.HTTP_409_CONFLICT)


class CategoriaViewSet(DaOrganizacaoMixin, viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer


class AutorViewSet(DaOrganizacaoMixin, viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer


class LivroViewSet(DaOrganizacaoMixin, viewsets.ModelViewSet):
    queryset = (Livro.objects.com_disponibilidade()
                .select_related('categoria').prefetch_related('autores'))
    serializer_class = LivroSerializer
