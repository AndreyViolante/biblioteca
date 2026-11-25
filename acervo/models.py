from django.core.validators import MinValueValidator, RegexValidator
from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=80, unique=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


class Autor(models.Model):
    nome = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'autores'

    def __str__(self):
        return self.nome


class Livro(models.Model):
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
