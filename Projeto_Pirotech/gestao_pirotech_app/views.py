from django.shortcuts import render
from .forms import CadastroForm, LoginForm
from django.contrib.auth.forms import UserCreationForm

def cadastro(request):
    form = CadastroForm()
    contexto = {'form': form}

    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            form.save()

    return render(request, 'gestao_pirotech_app/cadastro.html', contexto)