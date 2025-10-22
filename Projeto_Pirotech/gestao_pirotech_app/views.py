from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Usuarios, Produto, Vendas
from django.contrib.auth.decorators import login_required
from .forms import VendaForm, ProdutoForm
import pandas as pd
import plotly.express as px
import plotly.offline as op
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

def auxiliar_dados_por_usuario(request, model):
    if request.user.is_superuser:
        return model.objects.all()
    else:
        return model.objects.filter(usuario = request.user)


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
            return redirect('gestao-cadastro')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Este nome de usuário já está em uso!')
            return redirect('gestao-cadastro')


        user = User.objects.create_user(
            username=username, 
            email=email, 
            password=senha
        )

         
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

@login_required(login_url='gestao-login')
def estoque(request):
    user = request.user

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            form = ProdutoForm(request.POST)
            if form.is_valid():
                produto = form.save(commit=False)
                produto.usuario = user
                produto.save()
            else:
                messages.error(request, 'Erro ao criar o produto')

        elif action == "update":
            produto_id = request.POST.get('produto_id')
            produto = get_object_or_404(Produto, id = produto_id)

            if produto.usuario == user or user.is_superuser:
                form = ProdutoForm(request.POST, instance=produto)
                if form.is_valid():
                    form.save()
            else:
                messages.error(request, 'Ação não permitida')

        elif action == 'delete':
            produto_id = request.POST.get('produto_id')
            produto = get_object_or_404(Produto, id = produto_id)

            if produto.usuario == user or user.is_superuser:
                nome_produto = produto.nome
                produto.delete()
            else:
                messages.error(request, 'Ação não permitida')
        
        return redirect('gestao-estoque')
    
    else:
        produtos_do_usuario = auxiliar_dados_por_usuario(request, Produto).order_by('nome')
        form_criacao = ProdutoForm()

        contexto = {
            'produtos': produtos_do_usuario,
            'form_criacao': form_criacao,
            'tipo_cargo': 'admin' if user.is_superuser else user.perfil.cargo
        }


        return render(request, 'gestao_pirotech_app/estoque.html', contexto)

@login_required(login_url='gestao-login')
def vendas(request):
    user = request.user

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            form = VendaForm(user, request.POST)

            if form.is_valid():
                quantidade = form.cleaned_data['quantidade_vendida']
                produto_vendido = form.cleaned_data['produto']

                if produto_vendido.quantidade >= quantidade:
                    Vendas.objects.create(
                        produto = produto_vendido,
                        usuario = user,
                        quantidade_vendida = quantidade,
                        preco_unitario_venda = produto_vendido.preco,
                        custo_unitario_venda = produto_vendido.preco_de_custo,
                    )

                    produto_vendido.quantidade -= quantidade
                    produto_vendido.save()
                else:
                    messages.error(request, f'Estoque insuficiente para o cadastro da venda, existem apenas {produto_vendido.quantidade} unidades')
            else:
                messages.error(request, 'Erro ao registrar venda')
        return redirect('gestao-vendas')
    else:
        vendas_feitas = auxiliar_dados_por_usuario(request, Vendas)
        form_criacao = VendaForm(user=user)

        contexto = {
            'vendas': vendas_feitas,
            'form_criacao': form_criacao,
            'tipo_cargo': 'admin' if user.is_superuser else user.perfil.cargo,
        }
        return render(request, 'gestao_pirotech_app/vendas.html', contexto)

def fazer_logout(request):
    if request.method == 'POST':
        logout(request) 
        return redirect('gestao-login')
    return redirect('gestao-login')