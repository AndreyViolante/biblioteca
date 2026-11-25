from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from core.acesso import org_atual, papel_requerido, perfil_requerido

from .forms import AutorForm, CategoriaForm
from .models import Autor, Categoria


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
