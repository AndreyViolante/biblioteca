from datetime import timedelta

from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone

from core.models import DaOrganizacao

PRAZO_DIAS = 14


class Categoria(DaOrganizacao):
    nome = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Autor(DaOrganizacao):
    nome = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'autores'

    def __str__(self):
        return self.nome


class Livro(DaOrganizacao):
    titulo = models.CharField('título', max_length=200)
    isbn = models.CharField(
        'ISBN', max_length=13, unique=True,
        validators=[RegexValidator(r'^\d{13}$', 'O ISBN deve ter 13 dígitos.')])
    ano = models.PositiveIntegerField('ano de publicação')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    autores = models.ManyToManyField(Autor)
    exemplares = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['titulo']

    def __str__(self):
        return self.titulo


class Leitor(DaOrganizacao):
    nome = models.CharField(max_length=120)
    email = models.EmailField('e-mail', unique=True)
    telefone = models.CharField(max_length=20, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'leitores'

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
