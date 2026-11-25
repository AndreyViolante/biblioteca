from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from acervo.models import Emprestimo, Leitor, Livro

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


class PapeisTest(BaseTest):
    def test_sem_login_redireciona(self):
        for url in ('/dashboard/', '/livros/', '/leitores/', '/emprestimos/'):
            self.assertEqual(self.client.get(url).status_code, 302)

    def test_operador_nao_mexe_no_acervo(self):
        self.client.force_login(self.operador_a)
        self.assertEqual(self.client.get('/livros/novo/').status_code, 403)
        r = self.client.post(f'/livros/{self.livro_a.pk}/excluir/')
        self.assertEqual(r.status_code, 403)
        self.assertTrue(Livro.objects.filter(pk=self.livro_a.pk).exists())

    def test_operador_cadastra_leitor_e_empresta(self):
        self.client.force_login(self.operador_a)
        self.client.post('/leitores/novo/', {'nome': 'Z', 'email': 'z@exemplo.com', 'ativo': 'on'})
        self.assertEqual(Leitor.objects.get(nome='Z').organizacao, self.org_a)
        self.client.post('/emprestimos/novo/', {
            'livro': self.livro_a.pk, 'leitor': self.leitor_a.pk,
            'data_prevista': timezone.localdate() + timedelta(days=7)})
        self.assertEqual(Emprestimo.objects.get().organizacao, self.org_a)

    def test_superusuario_sem_perfil_recebe_aviso(self):
        self.client.force_login(User.objects.create_superuser('dono'))
        self.assertContains(self.client.get('/dashboard/'), 'sem perfil', status_code=403)

    def test_excluir_livro_em_uso_mostra_erro(self):
        self.emprestar(self.livro_a, self.leitor_a)
        self.client.force_login(self.admin_a)
        r = self.client.post(f'/livros/{self.livro_a.pk}/excluir/', follow=True)
        self.assertContains(r, 'está em uso')


class RegrasEmprestimoTest(BaseTest):
    def novo(self, livro=None, leitor=None):
        return Emprestimo(organizacao=self.org_a, livro=livro or self.livro_a,
                          leitor=leitor or self.leitor_a)

    def assertRecusado(self, emprestimo, campo):
        with self.assertRaises(ValidationError) as ctx:
            emprestimo.full_clean()
        self.assertIn(campo, ctx.exception.message_dict)

    def test_valido(self):
        self.novo().full_clean()

    def test_sem_exemplar_disponivel(self):
        outro = Leitor.objects.create(organizacao=self.org_a, nome='X', email='x@exemplo.com')
        self.emprestar(self.livro_a, outro)
        self.assertRecusado(self.novo(), 'livro')

    def test_leitor_inativo(self):
        self.leitor_a.ativo = False
        self.assertRecusado(self.novo(), 'leitor')

    def test_leitor_com_atraso(self):
        outro = self.criar_livro(self.org_a, 'Outro', '4444444444444')
        ontem = timezone.localdate() - timedelta(days=1)
        self.emprestar(outro, self.leitor_a, data_saida=ontem - timedelta(days=14),
                       data_prevista=ontem)
        self.assertRecusado(self.novo(), 'leitor')

    def test_limite_por_leitor(self):
        for i in range(3):
            self.emprestar(self.criar_livro(self.org_a, f'L{i}', f'555555555555{i}'), self.leitor_a)
        self.assertRecusado(self.novo(), 'leitor')

    def test_livro_de_outra_org(self):
        self.assertRecusado(self.novo(livro=self.livro_b), 'livro')

    def test_devolver_libera_o_exemplar_e_nao_repete(self):
        e = self.emprestar(self.livro_a, self.leitor_a)
        self.assertFalse(self.livro_a.disponivel)
        e.devolver()
        self.assertTrue(self.livro_a.disponivel)
        with self.assertRaises(ValidationError):
            e.devolver()
