from datetime import timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone

from core.models import DaOrganizacao

PRAZO_DIAS = 14
LIMITE_POR_LEITOR = 3


class Categoria(DaOrganizacao):
    unicos_por_org = ('nome',)
    nome = models.CharField(max_length=80)

    class Meta:
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'nome'], name='categoria_unica_por_org'),
        ]

    def __str__(self):
        return self.nome


class Autor(DaOrganizacao):
    unicos_por_org = ('nome',)
    nome = models.CharField(max_length=120)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'autores'
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'nome'], name='autor_unico_por_org'),
        ]

    def __str__(self):
        return self.nome


class LivroQuerySet(models.QuerySet):
    def com_disponibilidade(self):
        """Conta os empréstimos abertos na mesma consulta (evita N+1)."""
        return self.annotate(qtd_abertos=Count(
            'emprestimo', distinct=True,
            filter=Q(emprestimo__devolvido_em__isnull=True)
        )).order_by('titulo')  # o GROUP BY do annotate ignora o Meta.ordering


class Livro(DaOrganizacao):
    unicos_por_org = ('isbn',)

    titulo = models.CharField('título', max_length=200)
    isbn = models.CharField(
        'ISBN', max_length=13,
        validators=[RegexValidator(r'^\d{13}$', 'O ISBN deve ter 13 dígitos.')])
    ano = models.PositiveIntegerField('ano de publicação')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT)
    autores = models.ManyToManyField(Autor)
    exemplares = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    objects = LivroQuerySet.as_manager()

    class Meta:
        ordering = ['titulo']
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'isbn'], name='isbn_unico_por_org'),
        ]

    def __str__(self):
        return self.titulo

    @property
    def emprestados(self):
        # Usa o valor do annotate quando existe; senão, consulta o banco.
        if hasattr(self, 'qtd_abertos'):
            return self.qtd_abertos
        if not self.pk:
            return 0
        return self.emprestimo_set.filter(devolvido_em__isnull=True).count()

    @property
    def disponiveis(self):
        return max(self.exemplares - self.emprestados, 0)

    @property
    def disponivel(self):
        return self.disponiveis > 0

    def clean(self):
        super().clean()
        if self.ano and self.ano > timezone.localdate().year:
            raise ValidationError({'ano': 'O ano não pode estar no futuro.'})
        if self.exemplares is not None and self.exemplares < self.emprestados:
            raise ValidationError({
                'exemplares': f'Há {self.emprestados} exemplar(es) emprestado(s) agora.'})


class Leitor(DaOrganizacao):
    unicos_por_org = ('email',)

    nome = models.CharField(max_length=120)
    email = models.EmailField('e-mail')
    telefone = models.CharField(max_length=20, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['nome']
        verbose_name_plural = 'leitores'
        constraints = [
            models.UniqueConstraint(
                fields=['organizacao', 'email'], name='leitor_unico_por_org'),
        ]

    def __str__(self):
        return self.nome


def prazo_padrao():
    return timezone.localdate() + timedelta(days=PRAZO_DIAS)


class Emprestimo(DaOrganizacao):
    livro = models.ForeignKey(Livro, on_delete=models.PROTECT)
    leitor = models.ForeignKey(Leitor, on_delete=models.PROTECT)
    data_saida = models.DateField('saída', default=timezone.localdate)
    data_prevista = models.DateField('devolução prevista', default=prazo_padrao)
    devolvido_em = models.DateField('devolvido em', null=True, blank=True)

    class Meta:
        ordering = ['-data_saida', '-id']
        verbose_name = 'empréstimo'
        indexes = [models.Index(fields=['organizacao', 'data_saida'])]

    def __str__(self):
        return f'{self.livro} para {self.leitor}'

    @property
    def atrasado(self):
        return self.devolvido_em is None and self.data_prevista < timezone.localdate()

    @property
    def dias_atraso(self):
        fim = self.devolvido_em or timezone.localdate()
        return max((fim - self.data_prevista).days, 0)

    def clean(self):
        """Regras do empréstimo: valem no Admin, nos forms e na API."""
        super().clean()
        if not (self.livro_id and self.leitor_id):
            return
        if self.livro.organizacao_id != self.organizacao_id:
            raise ValidationError({'livro': 'Livro de outra organização.'})
        if self.leitor.organizacao_id != self.organizacao_id:
            raise ValidationError({'leitor': 'Leitor de outra organização.'})
        if self.data_prevista and self.data_prevista < self.data_saida:
            raise ValidationError({
                'data_prevista': 'A devolução não pode ser antes da saída.'})
        if self.pk is None:
            self._validar_novo()

    def _validar_novo(self):
        abertos = self.leitor.emprestimo_set.filter(devolvido_em__isnull=True)
        if not self.leitor.ativo:
            raise ValidationError({'leitor': 'Este leitor está inativo.'})
        if abertos.filter(data_prevista__lt=timezone.localdate()).exists():
            raise ValidationError({'leitor': 'Este leitor tem empréstimo atrasado.'})
        if abertos.count() >= LIMITE_POR_LEITOR:
            raise ValidationError({
                'leitor': f'Este leitor já tem {LIMITE_POR_LEITOR} empréstimos abertos.'})
        if abertos.filter(livro=self.livro).exists():
            raise ValidationError({'livro': 'O leitor já está com este livro.'})
        if not self.livro.disponivel:
            raise ValidationError({'livro': 'Não há exemplar disponível deste livro.'})

    def devolver(self):
        if self.devolvido_em:
            raise ValidationError('Este empréstimo já foi devolvido.')
        self.devolvido_em = timezone.localdate()
        self.save(update_fields=['devolvido_em'])
