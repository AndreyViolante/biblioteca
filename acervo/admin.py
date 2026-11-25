from django.contrib import admin

from .models import Autor, Categoria, Emprestimo, Leitor, Livro


@admin.register(Categoria, Autor)
class NomeAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)


@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'isbn', 'categoria', 'exemplares')
    list_filter = ('categoria',)
    list_select_related = ('categoria',)
    search_fields = ('titulo', 'isbn')


@admin.register(Leitor)
class LeitorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'email')


@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('livro', 'leitor', 'data_saida', 'data_prevista', 'devolvido_em')
    list_filter = ('data_saida',)
    list_select_related = ('livro', 'leitor')
