"""Métricas do dashboard. Usadas pela tela, pelo CSV e pela API."""
from django.db.models import Count, Q
from django.utils import timezone


def kpis(base):
    aberto = Q(devolvido_em__isnull=True)
    return base.aggregate(
        total=Count('id'),
        leitores=Count('leitor', distinct=True),
        abertos=Count('id', filter=aberto),
        atrasados=Count('id', filter=aberto & Q(data_prevista__lt=timezone.localdate())),
    )


def ranking_livros(base):
    """Quais livros mais saem?"""
    return list(
        base.values('livro__titulo')
        .annotate(total=Count('id'))
        .order_by('-total', 'livro__titulo')[:5])
