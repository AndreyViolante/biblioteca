from django.contrib.auth.models import User
from django.test import TestCase

from acervo.models import Autor, Categoria, Emprestimo, Leitor, Livro
from core.models import Organizacao, Perfil


class BaseTest(TestCase):
    """Duas organizações: A (admin e operador) e B (admin)."""

    @classmethod
    def setUpTestData(cls):
        cls.org_a = Organizacao.objects.create(nome='A')
        cls.org_b = Organizacao.objects.create(nome='B')
        cls.admin_a = cls.criar_usuario('admin_a', cls.org_a, Perfil.ADMIN)
        cls.operador_a = cls.criar_usuario('operador_a', cls.org_a, Perfil.OPERADOR)
        cls.admin_b = cls.criar_usuario('admin_b', cls.org_b, Perfil.ADMIN)
        cls.livro_a = cls.criar_livro(cls.org_a, 'Livro da A', '1111111111111')
        cls.livro_b = cls.criar_livro(cls.org_b, 'Livro da B', '2222222222222')
        cls.leitor_a = Leitor.objects.create(
            organizacao=cls.org_a, nome='Leitor A', email='a@exemplo.com')
        cls.leitor_b = Leitor.objects.create(
            organizacao=cls.org_b, nome='Leitor B', email='b@exemplo.com')

    @staticmethod
    def criar_usuario(nome, org, papel):
        usuario = User.objects.create_user(nome)
        Perfil.objects.create(usuario=usuario, organizacao=org, papel=papel)
        return usuario

    @staticmethod
    def criar_livro(org, titulo, isbn, exemplares=1):
        categoria, _ = Categoria.objects.get_or_create(organizacao=org, nome=f'Cat {org}')
        autor, _ = Autor.objects.get_or_create(organizacao=org, nome=f'Autor {org}')
        livro = Livro.objects.create(
            organizacao=org, titulo=titulo, isbn=isbn, ano=2000,
            categoria=categoria, exemplares=exemplares)
        livro.autores.add(autor)
        return livro

    @staticmethod
    def emprestar(livro, leitor, **extras):
        return Emprestimo.objects.create(
            organizacao=livro.organizacao, livro=livro, leitor=leitor, **extras)

    def dados_livro(self, livro, **extras):
        dados = {
            'titulo': 'Novo', 'isbn': '3333333333333', 'ano': 2001, 'exemplares': 1,
            'categoria': livro.categoria_id,
            'autores': [a.pk for a in livro.autores.all()],
        }
        dados.update(extras)
        return dados
