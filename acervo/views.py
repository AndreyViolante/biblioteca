import csv

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import ProtectedError, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.acesso import org_atual, papel_requerido, perfil_requerido

from . import dashboard as metricas
from .forms import (AutorForm, CategoriaForm, EmprestimoForm, FiltroLivroForm,
                    LeitorForm, LivroForm)
from .models import Autor, Categoria, Emprestimo, Leitor, Livro


# ---------- Funções comuns a todos os cadastros ----------

def _paginar(request, qs):
    pagina = Paginator(qs, 10).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)
    pagina.filtros = params.urlencode()  # mantém a busca ao trocar de página
    return pagina


def _salvar(request, form_class, rota, titulo, pk=None):
    org = org_atual(request)
    objeto = None
    if pk:
        # Registro de outra organização responde 404, como se não existisse.
        objeto = get_object_or_404(form_class.Meta.model, pk=pk, organizacao=org)
    form = form_class(request.POST or None, instance=objeto, org=org)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Registro salvo.')
        return redirect(rota)
    return render(request, 'acervo/form.html',
                  {'form': form, 'titulo': titulo, 'voltar': rota})


def _excluir(request, model, rota, pk):
    objeto = get_object_or_404(model, pk=pk, organizacao=org_atual(request))
    if request.method == 'POST':
        try:
            objeto.delete()
            messages.success(request, 'Registro excluído.')
        except ProtectedError:
            messages.error(request, f'"{objeto}" está em uso e não pode ser excluído.')
        return redirect(rota)
    return render(request, 'acervo/confirmar.html', {'objeto': objeto, 'voltar': rota})


# ---------- Livros ----------

@perfil_requerido
def lista_livros(request):
    org = org_atual(request)
    livros = (
        Livro.objects.filter(organizacao=org)
        .com_disponibilidade()
        .select_related('categoria')
        .prefetch_related('autores'))
    filtro = FiltroLivroForm(request.GET, org=org)
    if filtro.is_valid():
        q = filtro.cleaned_data['q']
        if q:
            livros = livros.filter(
                Q(titulo__icontains=q) | Q(isbn__icontains=q) | Q(autores__nome__icontains=q))
        if filtro.cleaned_data['categoria']:
            livros = livros.filter(categoria=filtro.cleaned_data['categoria'])
    return render(request, 'acervo/livros.html',
                  {'pagina': _paginar(request, livros), 'filtro': filtro})


@papel_requerido('admin')
def novo_livro(request):
    return _salvar(request, LivroForm, 'livros', 'Novo livro')


@papel_requerido('admin')
def editar_livro(request, pk):
    return _salvar(request, LivroForm, 'livros', 'Editar livro', pk)


@papel_requerido('admin')
def excluir_livro(request, pk):
    return _excluir(request, Livro, 'livros', pk)


# ---------- Categorias e autores ----------

@perfil_requerido
def lista_categorias(request):
    qs = Categoria.objects.filter(organizacao=org_atual(request))
    return render(request, 'acervo/nomes.html', {
        'pagina': _paginar(request, qs), 'titulo': 'Categorias',
        'rota_nova': 'nova_categoria', 'rota_editar': 'editar_categoria',
        'rota_excluir': 'excluir_categoria'})


@papel_requerido('admin')
def nova_categoria(request):
    return _salvar(request, CategoriaForm, 'categorias', 'Nova categoria')


@papel_requerido('admin')
def editar_categoria(request, pk):
    return _salvar(request, CategoriaForm, 'categorias', 'Editar categoria', pk)


@papel_requerido('admin')
def excluir_categoria(request, pk):
    return _excluir(request, Categoria, 'categorias', pk)


@perfil_requerido
def lista_autores(request):
    qs = Autor.objects.filter(organizacao=org_atual(request))
    return render(request, 'acervo/nomes.html', {
        'pagina': _paginar(request, qs), 'titulo': 'Autores',
        'rota_nova': 'novo_autor', 'rota_editar': 'editar_autor',
        'rota_excluir': 'excluir_autor'})


@papel_requerido('admin')
def novo_autor(request):
    return _salvar(request, AutorForm, 'autores', 'Novo autor')


@papel_requerido('admin')
def editar_autor(request, pk):
    return _salvar(request, AutorForm, 'autores', 'Editar autor', pk)


@papel_requerido('admin')
def excluir_autor(request, pk):
    return _excluir(request, Autor, 'autores', pk)


# ---------- Leitores (operador cadastra e edita; só admin exclui) ----------

@perfil_requerido
def lista_leitores(request):
    qs = Leitor.objects.filter(organizacao=org_atual(request))
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(nome__icontains=q) | Q(email__icontains=q))
    return render(request, 'acervo/leitores.html', {'pagina': _paginar(request, qs), 'q': q})


@perfil_requerido
def novo_leitor(request):
    return _salvar(request, LeitorForm, 'leitores', 'Novo leitor')


@perfil_requerido
def editar_leitor(request, pk):
    return _salvar(request, LeitorForm, 'leitores', 'Editar leitor', pk)


@papel_requerido('admin')
def excluir_leitor(request, pk):
    return _excluir(request, Leitor, 'leitores', pk)


# ---------- Empréstimos ----------

@perfil_requerido
def lista_emprestimos(request):
    qs = (Emprestimo.objects.filter(organizacao=org_atual(request))
          .select_related('livro', 'leitor'))
    situacao = request.GET.get('situacao', 'abertos')
    if situacao == 'abertos':
        qs = qs.filter(devolvido_em__isnull=True)
    elif situacao == 'atrasados':
        qs = qs.filter(devolvido_em__isnull=True, data_prevista__lt=timezone.localdate())
    elif situacao == 'devolvidos':
        qs = qs.filter(devolvido_em__isnull=False)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(livro__titulo__icontains=q) | Q(leitor__nome__icontains=q))
    return render(request, 'acervo/emprestimos.html', {
        'pagina': _paginar(request, qs), 'situacao': situacao, 'q': q,
        'situacoes': [('abertos', 'Abertos'), ('atrasados', 'Atrasados'),
                      ('devolvidos', 'Devolvidos'), ('todos', 'Todos')]})


@perfil_requerido
def novo_emprestimo(request):
    return _salvar(request, EmprestimoForm, 'emprestimos', 'Novo empréstimo')


@perfil_requerido
@require_POST
def devolver_emprestimo(request, pk):
    emprestimo = get_object_or_404(Emprestimo, pk=pk, organizacao=org_atual(request))
    try:
        emprestimo.devolver()
        messages.success(request, f'"{emprestimo.livro}" devolvido.')
    except ValidationError as erro:
        messages.error(request, erro.messages[0])
    return redirect('emprestimos')


@papel_requerido('admin')
def excluir_emprestimo(request, pk):
    return _excluir(request, Emprestimo, 'emprestimos', pk)


# ---------- Dashboard e relatório ----------

@perfil_requerido
def dashboard(request):
    org = org_atual(request)
    base, form = metricas.emprestimos_do_periodo(request, org)
    contexto = {
        'form': form,
        'kpis': metricas.kpis(base),
        'ranking': metricas.ranking_livros(base),
        'por_categoria': metricas.por_categoria(base),
        'atrasados': metricas.atrasados(org),
        'mostra_series': request.user.perfil.eh_admin,
    }
    if contexto['mostra_series']:
        contexto['por_mes'] = metricas.por_mes(base)
    return render(request, 'acervo/dashboard.html', contexto)


def _celula(texto):
    """Impede que o Excel interprete o texto como fórmula."""
    return "'" + texto if texto.startswith(('=', '+', '-', '@')) else texto


@papel_requerido('admin')
def exportar_csv(request):
    base, _ = metricas.emprestimos_do_periodo(request, org_atual(request))
    resposta = HttpResponse(content_type='text/csv; charset=utf-8')
    resposta['Content-Disposition'] = 'attachment; filename="emprestimos.csv"'
    resposta.write('\ufeff')  # BOM: o Excel reconhece os acentos
    escritor = csv.writer(resposta, delimiter=';')
    escritor.writerow(['Livro', 'Leitor', 'Saída', 'Prevista', 'Devolvido em'])
    for e in base.select_related('livro', 'leitor'):
        escritor.writerow([
            _celula(e.livro.titulo), _celula(e.leitor.nome),
            e.data_saida, e.data_prevista, e.devolvido_em or ''])
    return resposta
