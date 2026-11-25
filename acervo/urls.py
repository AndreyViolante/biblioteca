from django.urls import path

from . import views

urlpatterns = [
    path('livros/', views.lista_livros, name='livros'),
    path('livros/novo/', views.novo_livro, name='novo_livro'),
    path('livros/<int:pk>/editar/', views.editar_livro, name='editar_livro'),
    path('livros/<int:pk>/excluir/', views.excluir_livro, name='excluir_livro'),

    path('categorias/', views.lista_categorias, name='categorias'),
    path('categorias/nova/', views.nova_categoria, name='nova_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/excluir/', views.excluir_categoria, name='excluir_categoria'),

    path('autores/', views.lista_autores, name='autores'),
    path('autores/novo/', views.novo_autor, name='novo_autor'),
    path('autores/<int:pk>/editar/', views.editar_autor, name='editar_autor'),
    path('autores/<int:pk>/excluir/', views.excluir_autor, name='excluir_autor'),

    path('leitores/', views.lista_leitores, name='leitores'),
    path('leitores/novo/', views.novo_leitor, name='novo_leitor'),
    path('leitores/<int:pk>/editar/', views.editar_leitor, name='editar_leitor'),
    path('leitores/<int:pk>/excluir/', views.excluir_leitor, name='excluir_leitor'),

    path('emprestimos/', views.lista_emprestimos, name='emprestimos'),
    path('emprestimos/novo/', views.novo_emprestimo, name='novo_emprestimo'),
    path('emprestimos/<int:pk>/excluir/', views.excluir_emprestimo, name='excluir_emprestimo'),
]
