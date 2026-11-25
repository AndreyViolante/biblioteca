from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import api_views

router = DefaultRouter()
router.register('livros', api_views.LivroViewSet)
router.register('categorias', api_views.CategoriaViewSet)
router.register('autores', api_views.AutorViewSet)
router.register('leitores', api_views.LeitorViewSet)
router.register('emprestimos', api_views.EmprestimoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
