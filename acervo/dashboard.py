"""Métricas do dashboard. Usadas pela tela, pelo CSV e pela API."""
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from .forms import PeriodoForm
from .models import Emprestimo


def emprestimos_do_periodo(request, org):
    """Base de toda métrica: já filtrada por organização e período."""
    qs = Emprestimo.objects.filter(organizacao=org)
    form = PeriodoForm(request.GET)
    if form.is_valid():
        if form.cleaned_data['inicio']:
            qs = qs.filter(data_saida__gte=form.cleaned_data['inicio'])
        if form.cleaned_data['fim']:
            qs = qs.filter(data_saida__lte=form.cleaned_data['fim'])
    return qs, form


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


def por_mes(base):
    """Como os empréstimos evoluem mês a mês?"""
    linhas = (
        base.annotate(mes=TruncMonth('data_saida'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes'))
    return [{'rotulo': r['mes'].strftime('%m/%Y'), 'total': r['total']} for r in linhas]


def por_categoria(base):
    """Qual categoria é mais procurada?"""
    linhas = (
        base.values('livro__categoria__nome')
        .annotate(total=Count('id'))
        .order_by('-total', 'livro__categoria__nome'))
    return [{'rotulo': r['livro__categoria__nome'], 'total': r['total']} for r in linhas]
