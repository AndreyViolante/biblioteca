from django import forms

from .models import Autor, Categoria, Livro


class FormDaOrganizacao(forms.ModelForm):
    """Base dos forms: fixa a organização e filtra os selects por ela."""

    def __init__(self, *args, org, **kwargs):
        super().__init__(*args, **kwargs)
        # A organização não é campo do form: vem da view (usuário logado).
        self.instance.organizacao = org
        for campo in self.fields.values():
            if isinstance(campo, forms.ModelChoiceField):  # cobre FK e M2M
                campo.queryset = campo.queryset.filter(organizacao=org)


class CategoriaForm(FormDaOrganizacao):
    class Meta:
        model = Categoria
        fields = ['nome']


class AutorForm(FormDaOrganizacao):
    class Meta:
        model = Autor
        fields = ['nome']


class LivroForm(FormDaOrganizacao):
    class Meta:
        model = Livro
        fields = ['titulo', 'isbn', 'ano', 'categoria', 'autores', 'exemplares']
        widgets = {'autores': forms.CheckboxSelectMultiple}
