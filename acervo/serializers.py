import copy

from django.core.exceptions import ValidationError as ErroDjango
from rest_framework import serializers

from core.acesso import org_atual

from .models import Autor, Categoria


class SerializerDaOrganizacao(serializers.ModelSerializer):
    """Filtra os ids relacionados pela organização e reusa o clean() do model."""

    def get_fields(self):
        campos = super().get_fields()
        org = org_atual(self.context['request'])
        for campo in campos.values():
            relacao = getattr(campo, 'child_relation', campo)  # M2M ou FK
            if getattr(relacao, 'queryset', None) is not None:
                relacao.queryset = relacao.queryset.filter(organizacao=org)
        return campos

    def validate(self, dados):
        model = self.Meta.model
        m2m = {f.name for f in model._meta.many_to_many}
        objeto = copy.copy(self.instance) if self.instance else model()
        objeto.organizacao = org_atual(self.context['request'])
        for nome, valor in dados.items():
            if nome not in m2m:
                setattr(objeto, nome, valor)
        try:
            objeto.full_clean()
        except ErroDjango as erro:
            raise serializers.ValidationError(erro.message_dict)
        return dados


class CategoriaSerializer(SerializerDaOrganizacao):
    class Meta:
        model = Categoria
        fields = ['id', 'nome']


class AutorSerializer(SerializerDaOrganizacao):
    class Meta:
        model = Autor
        fields = ['id', 'nome']
