import random
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from acervo.models import Autor, Categoria, Emprestimo, Leitor, Livro
from core.models import Organizacao, Perfil

SENHA_DEMO = 'biblioteca2026'  # só para demonstração local

USUARIOS = [  # usuário, organização, papel
    ('ana', 'Biblioteca Central', Perfil.ADMIN),
    ('carla', 'Biblioteca Central', Perfil.OPERADOR),
    ('bruno', 'Biblioteca do Bairro', Perfil.ADMIN),
]

LIVROS = [  # título, autor, categoria, ano
    ('Dom Casmurro', 'Machado de Assis', 'Romance', 1899),
    ('Memórias Póstumas de Brás Cubas', 'Machado de Assis', 'Romance', 1881),
    ('O Cortiço', 'Aluísio Azevedo', 'Romance', 1890),
    ('Iracema', 'José de Alencar', 'Romance', 1865),
    ('Vidas Secas', 'Graciliano Ramos', 'Romance', 1938),
    ('Capitães da Areia', 'Jorge Amado', 'Romance', 1937),
    ('A Hora da Estrela', 'Clarice Lispector', 'Romance', 1977),
    ('Antologia Poética', 'Carlos Drummond de Andrade', 'Poesia', 1962),
    ('Libertinagem', 'Manuel Bandeira', 'Poesia', 1930),
    ('Sagarana', 'João Guimarães Rosa', 'Contos', 1946),
    ('Laços de Família', 'Clarice Lispector', 'Contos', 1960),
    ('Os Sertões', 'Euclides da Cunha', 'História', 1902),
]

LEITORES = ['Alice Moura', 'Beatriz Lima', 'Caio Nunes', 'Davi Rocha', 'Elisa Prado',
            'Fábio Reis', 'Gabriela Luz', 'Hugo Teles', 'Isabel Faria', 'João Matos']


class Command(BaseCommand):
    help = 'Cria duas bibliotecas com dados fictícios para demonstração.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Este comando só roda com DEBUG=True.')
        if Organizacao.objects.filter(nome__in=[u[1] for u in USUARIOS]).exists():
            raise CommandError('Os dados de demonstração já existem.')

        for nome, org_nome, papel in USUARIOS:
            org, criada = Organizacao.objects.get_or_create(nome=org_nome)
            usuario = User.objects.create_user(nome, password=SENHA_DEMO, first_name=nome.title())
            Perfil.objects.create(usuario=usuario, organizacao=org, papel=papel)
            if criada:
                central = org_nome == 'Biblioteca Central'
                self._popular(org, LIVROS if central else LIVROS[4:], 110 if central else 40)

        self.stdout.write(self.style.SUCCESS(
            'Pronto: usuários ana, carla e bruno (senha em popular_demo.py).'))

    def _popular(self, org, livros_base, quantidade):
        sorteio = random.Random(org.nome)  # mesma semente, mesmos dados
        hoje = timezone.localdate()
        livros, leitores = [], []
        for i, (titulo, autor, categoria, ano) in enumerate(livros_base):
            cat, _ = Categoria.objects.get_or_create(organizacao=org, nome=categoria)
            aut, _ = Autor.objects.get_or_create(organizacao=org, nome=autor)
            livro = Livro.objects.create(
                organizacao=org, titulo=titulo, isbn=f'97885000{i:05d}', ano=ano,
                categoria=cat, exemplares=sorteio.randint(1, 3))
            livro.autores.add(aut)
            livros.append(livro)
        for nome in LEITORES:
            email = nome.lower().replace(' ', '.').replace('á', 'a').replace('ã', 'a')
            leitores.append(Leitor.objects.create(
                organizacao=org, nome=nome, email=f'{email}@exemplo.com'))

        # Histórico já devolvido, espalhado pelos últimos 7 meses.
        pesos = range(len(livros), 0, -1)
        for _ in range(quantidade):
            saida = hoje - timedelta(days=sorteio.randint(30, 210))
            Emprestimo.objects.create(
                organizacao=org, livro=sorteio.choices(livros, pesos)[0],
                leitor=sorteio.choice(leitores), data_saida=saida,
                data_prevista=saida + timedelta(days=14),
                devolvido_em=saida + timedelta(days=sorteio.randint(3, 18)))
        # Abertos: um livro por leitor; os dois primeiros estão atrasados.
        for i, (livro, leitor) in enumerate(zip(livros[:6], leitores)):
            saida = hoje - timedelta(days=20 + i if i < 2 else i)
            Emprestimo.objects.create(
                organizacao=org, livro=livro, leitor=leitor, data_saida=saida,
                data_prevista=saida + timedelta(days=14))
