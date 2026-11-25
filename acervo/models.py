from datetime import timedelta

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from core.models import DaOrganizacao

PRAZO_DIAS = 14


class Categoria(DaOrganizacao):
    unicos_por_org = ('nome',)
    nome = models.CharField(max_length=80)

    class Meta:
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'nome'], name='categoria_unica_por_org'),
        ]

    def __str__(self):
        return self.nome


class Autor(DaOrganizacao):
    unicos_por_org = ('nome',)
    nome = models.CharField(max_length=120)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'autores'
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'nome'], name='autor_unico_por_org'),
        ]

    def __str__(self):
        return self.nome


class Livro(DaOrganizacao):
    unicos_por_org = ('isbn',)

    titulo = models.CharField('título', max_length=200)
    isbn = models.CharField(
        'ISBN', max_length=13,
        validators=[RegexValidator(r'^\d{13}$', 'O ISBN deve ter 13 dígitos.')])
    ano = models.PositiveIntegerField('ano de publicação')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    autores = models.ManyToManyField(Autor)
    exemplares = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['titulo']
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'isbn'], name='isbn_unico_por_org'),
        ]

    def __str__(self):
        return self.titulo


class Leitor(DaOrganizacao):
    unicos_por_org = ('email',)

    nome = models.CharField(max_length=120)
    email = models.EmailField('e-mail')
    telefone = models.CharField(max_length=20, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'leitores'
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'email'], name='leitor_unico_por_org'),
        ]

    def __str__(self):
        return self.nome


def prazo_padrao():
    return timezone.localdate() + timedelta(days=PRAZO_DIAS)


class Emprestimo(DaOrganizacao):
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT)
    leitor = models.ForeignKey(Leitor, on_delete=models.PROTECT)
    data_saida = models.DateField('saída', default=timezone.localdate)
    data_prevista = models.DateField('devolução prevista', default=prazo_padrao)
    devolvido_em = models.DateField('devolvido em', null=True, blank=True)

    class Meta:
        ordering = ['-data_saida', '-id']
        verbose_name = 'empréstimo'

    def __str__(self):
        return f'{self.livro} para {self.leitor}'
