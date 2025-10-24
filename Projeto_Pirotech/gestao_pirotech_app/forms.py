from django import forms
from .models import Produto, Vendas

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['animal', 'preco', 'preco_de_custo', 'quantidade', 'tipo', 'peso']

class VendaForm(forms.ModelForm):
    class Meta:
        model = Vendas
        fields = ['produto', 'quantidade_vendida']

    def __init__(self, user, *args, **kwargs):
        super(VendaForm, self).__init__(*args, **kwargs)
        self.fields['produto'].queryset = Produto.objects.filter(usuario=user)
    