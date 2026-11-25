from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models


class Organizacao(models.Model):
    """O "inquilino" do sistema: cada biblioteca é dona dos seus dados."""

    nome = models.CharField(max_length=120, unique=True)
    criada_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'organização'
        verbose_name_plural = 'organizações'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class DaOrganizacao(models.Model):
    """Base abstrata: todo model de negócio pertence a uma organização."""

    # Campos que não podem se repetir DENTRO da mesma organização.
    unicos_por_org = ()

    organizacao = models.ForeignKey(
        Organizacao, on_delete=models.PROTECT, verbose_name='organização')

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        erros = {}
        for campo in self.unicos_por_org:
            valor = getattr(self, campo)
            repetidos = type(self).objects.filter(
                organizacao_id=self.organizacao_id, **{campo: valor})
            if valor and repetidos.exclude(pk=self.pk).exists():
                rotulo = self._meta.get_field(campo).verbose_name
                erros[campo] = f'Já existe um cadastro com este {rotulo} na sua organização.'
        if erros:
            raise ValidationError(erros)


class Perfil(models.Model):
    """Liga o usuário a UMA organização."""

    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='usuário')
    organizacao = models.ForeignKey(
        Organizacao, on_delete=models.PROTECT, verbose_name='organização')

    class Meta:
        verbose_name_plural = 'perfis'

    def __str__(self):
        return f'{self.usuario} ({self.organizacao})'
