from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

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
            return redirect('cadastro')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já está em uso!')
            return redirect('cadastro')

        user = User.objects.create_user(username=username, email=email, password=senha)
        
        return redirect('login')
    
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = authenticate(username=username, password=senha)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, f"Usuário ou senha inválidos, tente novamente!")
            return redirect("login")
    else:
        return render(request, "gestao_pirotech_app/login.html")