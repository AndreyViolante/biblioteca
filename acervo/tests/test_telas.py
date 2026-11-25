from acervo.models import Livro

from .base import BaseTest


class IsolamentoTest(BaseTest):
    """Roteiro de testes da Aula 14."""

    def setUp(self):
        self.client.force_login(self.admin_a)

    def test_lista_so_livros_da_organizacao(self):
        r = self.client.get('/livros/')
        self.assertContains(r, 'Livro da A')
        self.assertNotContains(r, 'Livro da B')

    def test_editar_e_excluir_de_outra_org_da_404(self):
        for rota in ('editar', 'excluir'):
            r = self.client.get(f'/livros/{self.livro_b.pk}/{rota}/')
            self.assertEqual(r.status_code, 404)

    def test_devolver_emprestimo_de_outra_org_da_404(self):
        e = self.emprestar(self.livro_b, self.leitor_b)
        r = self.client.post(f'/emprestimos/{e.pk}/devolver/')
        self.assertEqual(r.status_code, 404)
        e.refresh_from_db()
        self.assertIsNone(e.devolvido_em)

    def test_livro_criado_na_org_do_usuario(self):
        # Mesmo forçando outra organização no POST, vale a do usuário logado.
        self.client.post('/livros/novo/', self.dados_livro(
            self.livro_a, organizacao=self.org_b.pk))
        self.assertEqual(Livro.objects.get(isbn='3333333333333').organizacao, self.org_a)

    def test_selects_so_com_opcoes_da_org(self):
        form = self.client.get('/livros/novo/').context['form']
        self.assertEqual(list(form.fields['categoria'].queryset), [self.livro_a.categoria])
        form = self.client.get('/emprestimos/novo/').context['form']
        self.assertEqual(list(form.fields['leitor'].queryset), [self.leitor_a])

    def test_isbn_unico_por_organizacao(self):
        dados = self.dados_livro(self.livro_a, isbn=self.livro_b.isbn)
        self.assertRedirects(self.client.post('/livros/novo/', dados), '/livros/')
        # Repetido dentro da própria organização: erro no campo, sem IntegrityError.
        r = self.client.post('/livros/novo/', dados)
        self.assertIn('isbn', r.context['form'].errors)
