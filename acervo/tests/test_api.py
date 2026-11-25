from acervo.models import Emprestimo, Livro

from .base import BaseTest


class ApiTest(BaseTest):
    def entrar(self, usuario):
        self.client.force_login(usuario)

    def enviar(self, url, dados, metodo='post'):
        return getattr(self.client, metodo)(url, dados, content_type='application/json')

    def test_sem_login_e_bloqueada(self):
        self.assertEqual(self.client.get('/api/livros/').status_code, 403)

    def test_lista_e_detalhe_so_da_organizacao(self):
        self.entrar(self.admin_a)
        dados = self.client.get('/api/livros/').json()
        self.assertEqual([x['titulo'] for x in dados['results']], ['Livro da A'])
        self.assertEqual(self.client.get(f'/api/livros/{self.livro_b.pk}/').status_code, 404)

    def test_crud_do_admin(self):
        self.entrar(self.admin_a)
        r = self.enviar('/api/livros/', self.dados_livro(self.livro_a))
        self.assertEqual(r.status_code, 201, r.content)
        livro = Livro.objects.get(pk=r.json()['id'])
        self.assertEqual(livro.organizacao, self.org_a)
        url = f'/api/livros/{livro.pk}/'
        r = self.enviar(url, {'titulo': 'Mudou'}, 'patch')
        self.assertEqual((r.status_code, r.json()['titulo']), (200, 'Mudou'))
        self.assertEqual(self.client.delete(url).status_code, 204)

    def test_validacao_do_model_vira_400(self):
        self.entrar(self.admin_a)
        for isbn in ('123', self.livro_a.isbn):  # curto e repetido
            r = self.enviar('/api/livros/', self.dados_livro(self.livro_a, isbn=isbn))
            self.assertEqual(r.status_code, 400)
            self.assertIn('isbn', r.json())

    def test_nao_aceita_ids_de_outra_org(self):
        self.entrar(self.admin_a)
        r = self.enviar('/api/livros/', self.dados_livro(self.livro_b))
        self.assertEqual(set(r.json()), {'categoria', 'autores'})
        r = self.enviar('/api/emprestimos/', {
            'livro': self.livro_b.pk, 'leitor': self.leitor_b.pk})
        self.assertEqual(set(r.json()), {'livro', 'leitor'})

    def test_operador_le_e_empresta_mas_nao_altera_acervo(self):
        self.entrar(self.operador_a)
        self.assertEqual(self.client.get('/api/livros/').status_code, 200)
        r = self.enviar('/api/livros/', self.dados_livro(self.livro_a))
        self.assertEqual(r.status_code, 403)
        r = self.enviar('/api/emprestimos/', {
            'livro': self.livro_a.pk, 'leitor': self.leitor_a.pk})
        self.assertEqual(r.status_code, 201, r.content)
        url = f"/api/emprestimos/{r.json()['id']}/"
        self.assertEqual(self.client.delete(url).status_code, 403)
        self.assertEqual(self.client.post(url + 'devolver/').status_code, 200)
        self.assertEqual(self.client.post(url + 'devolver/').status_code, 400)
        self.assertIsNotNone(Emprestimo.objects.get().devolvido_em)

    def test_excluir_em_uso_da_409(self):
        self.emprestar(self.livro_a, self.leitor_a)
        self.entrar(self.admin_a)
        r = self.client.delete(f'/api/livros/{self.livro_a.pk}/')
        self.assertEqual(r.status_code, 409)

    def test_dashboard(self):
        self.emprestar(self.livro_a, self.leitor_a)
        self.emprestar(self.livro_b, self.leitor_b)
        self.entrar(self.admin_a)
        dados = self.client.get('/api/dashboard/').json()
        self.assertEqual(dados['kpis']['total'], 1)
        self.assertIn('por_mes', dados)
        self.assertEqual(self.client.get('/api/dashboard/?inicio=abc').status_code, 400)
        self.entrar(self.operador_a)
        self.assertNotIn('por_mes', self.client.get('/api/dashboard/').json())
