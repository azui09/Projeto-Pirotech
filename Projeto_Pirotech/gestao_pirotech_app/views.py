from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Usuarios, Produto, Vendas
from django.contrib.auth.decorators import login_required

def cadastro(request):
    if request.method == 'GET':
        return render(request, "gestao_pirotech_app/cadastro.html")
    else:
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            messages.error(request, 'As senhas não coincidem!')
            return redirect('getsao-cadastro')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já está em uso!')
            return redirect('gestao-cadastro')

        user = User.objects.create_user(username=username, email=email, password=senha)

        Usuarios.objects.create(
            user=user,
            cargo='vendedor',
        )
        
        return redirect('gestao-login')
    
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)
        if user is not None:
            auth_login(request, user)
            return redirect('gestao-dashboard')
        else:
            messages.error(request, f"Usuário ou senha inválidos, tente novamente!")
            return redirect("gestao-login")
    else:
        return render(request, "gestao_pirotech_app/login.html")

@login_required(login_url='gestao-login')
def dashboard(request):
    if request.user.is_superuser:
        produtos = Produto.objects.all()
        vendas = Vendas.objects.all()
        tipo_cargo = 'admin'
    else:
        produtos = Produto.objects.filter(usuario=request.user)
        vendas = Vendas.objects.filter(usuario=request.user)
        tipo_cargo = request.user.perfil.cargo

    contexto = {
        'produtos': produtos,
        'vendas': vendas,
        'tipo_cargo': tipo_cargo
    }

    return render(request, "gestao_pirotech_app/dashboard.html", contexto)

def vendas(request):
    return render(request, 'gestao_pirotech_app/vendas.html')

def estoque(request):
    return render(request, 'gestao_pirotech_app/estoque.html')

def fazer_logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('gestao-login')
    return redirect('gestao-login')