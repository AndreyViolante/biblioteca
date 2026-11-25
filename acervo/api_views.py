from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.acesso import org_atual

from .models import Autor, Categoria, Emprestimo, Leitor, Livro
from .serializers import (AutorSerializer, CategoriaSerializer,
                          EmprestimoSerializer, LeitorSerializer, LivroSerializer)


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


class LeitorViewSet(DaOrganizacaoMixin, viewsets.ModelViewSet):
    queryset = Leitor.objects.all()
    serializer_class = LeitorSerializer
    operador_pode = ('create', 'update', 'partial_update')


class EmprestimoViewSet(DaOrganizacaoMixin, mixins.CreateModelMixin,
                        mixins.RetrieveModelMixin, mixins.ListModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """Sem PUT/PATCH: um empréstimo só muda pela devolução."""

    queryset = Emprestimo.objects.select_related('livro', 'leitor')
    serializer_class = EmprestimoSerializer
    operador_pode = ('create', 'devolver')

    @action(detail=True, methods=['post'])
    def devolver(self, request, pk=None):
        emprestimo = self.get_object()
        try:
            emprestimo.devolver()
        except ValidationError as erro:
            return Response({'detail': erro.messages[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(self.get_serializer(emprestimo).data)
