from django.contrib import admin

from .models import Autor, Categoria, Emprestimo, Leitor, Livro


@admin.register(Categoria, Autor)
class NomeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'organizacao')
    list_filter = ('organizacao',)
    search_fields = ('nome',)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'isbn', 'categoria', 'exemplares', 'organizacao')
    list_filter = ('organizacao', 'categoria')
    list_select_related = ('categoria', 'organizacao')
    search_fields = ('titulo', 'isbn')


@admin.register(Leitor)
class LeitorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'ativo', 'organizacao')
    list_filter = ('organizacao', 'ativo')
    search_fields = ('nome', 'email')


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('livro', 'leitor', 'data_saida', 'data_prevista', 'devolvido_em', 'organizacao')
    list_filter = ('organizacao', 'data_saida')
    list_select_related = ('livro', 'leitor', 'organizacao')
