from django.urls import path

from . import views

urlpatterns = [
    path('categorias/', views.lista_categorias, name='categorias'),
    path('categorias/nova/', views.nova_categoria, name='nova_categoria'),
    path('categorias/<int:pk>/editar/', views.editar_categoria, name='editar_categoria'),
    path('categorias/<int:pk>/excluir/', views.excluir_categoria, name='excluir_categoria'),
]
