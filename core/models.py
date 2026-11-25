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
