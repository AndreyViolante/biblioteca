from django.db import migrations

MODELS = ['Categoria', 'Autor', 'Livro', 'Leitor', 'Emprestimo']


def org_padrao(apps, schema_editor):
    Organizacao = apps.get_model('core', 'Organizacao')
    for nome in MODELS:
        sem_org = apps.get_model('acervo', nome).objects.filter(organizacao__isnull=True)
        if sem_org.exists():
            org, _ = Organizacao.objects.get_or_create(nome='Organização padrão')
            sem_org.update(organizacao=org)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_organizacao'),
        ('acervo', '0006_organizacao_nula'),
    ]

    operations = [migrations.RunPython(org_padrao, migrations.RunPython.noop)]
