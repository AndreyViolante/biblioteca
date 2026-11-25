from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase


class MigracaoOrganizacaoTest(TransactionTestCase):
    """Dados anteriores à multi-organização não se perdem (Aula 14)."""

    def migrar(self, nome):
        alvo = [('acervo', nome)]
        executor = MigrationExecutor(connection)
        executor.migrate(alvo)
        return executor.loader.project_state(alvo).apps

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def test_registro_antigo_recebe_organizacao_padrao(self):
        apps = self.migrar('0005_emprestimo')
        apps.get_model('acervo', 'Categoria').objects.create(nome='Romance')

        apps = self.migrar('0008_organizacao_obrigatoria')
        categoria = apps.get_model('acervo', 'Categoria').objects.get(nome='Romance')
        self.assertEqual(categoria.organizacao.nome, 'Organização padrão')
