from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Usuarios, Produto, Vendas, catalogo_racoes
from django.contrib.auth.decorators import login_required
from .forms import VendaForm, ProdutoForm
import pandas as pd
import plotly.express as px
import plotly.offline as op

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
    user = request.user
    contexto = {'tipo_cargo': 'admin' if user.is_superuser else user.perfil.cargo}

    graficos = []
    kpis = {}

    if user.is_superuser:
        vendas_queryset = Vendas.objects.all()
        produtos_queryset = Produto.objects.all()

        vendas_data = list(vendas_queryset.values(
            'usuario__username', 'quantidade_vendida',
            'preco_unitario_venda', 'custo_unitario_venda',
            'produto__tipo'
        ))

        if not vendas_data:
            graficos.append('<p>Ainda não há dados de vendas na plataforma.</p>')
            kpis = {
                'Receita Total': 0, 'Lucro Total': 0,
                'Total Vendedores': Usuarios.objects.filter(cargo='vendedor').count(),
                'Total Produtos': produtos_queryset.count()
            }
        else:
            df = pd.DataFrame.from_records(vendas_data)
            df['receita'] = df['quantidade_vendida'] * df['preco_unitario_venda']
            df['lucro'] = df['quantidade_vendida'] * (df['preco_unitario_venda'] - df['custo_unitario_venda'])

            kpis = {
                'Receita Total': df['receita'].sum(), 'Lucro Total': df['lucro'].sum(),
                'Total Vendedores': Usuarios.objects.filter(cargo='vendedor').count(),
                'Total Produtos': produtos_queryset.count()
            }

            df_vendedores = df.groupby('usuario__username')[['receita', 'lucro']].sum().reset_index()

            fig1 = px.scatter(
                df_vendedores,
                x='receita',
                y='lucro',
                title='Performance dos Vendedores (Receita vs. Lucro)',
                text='usuario__username',
                labels={'receita': 'Receita Total (R$)', 'lucro': 'Lucro Total (R$)'},
                template='plotly_dark'
            )

            fig1.update_layout(title_x=0.5)
            fig1.update_traces(textposition='top center')
            graficos.append(op.plot(fig1, output_type='div', include_plotlyjs=False))

            fig2 = px.pie(
                df_vendedores,
                names='usuario__username',
                values='receita',
                title='Market Share (Fatia de Receita por Vendedor)',
                template='plotly_dark'
            )

            fig2.update_layout(title_x=0.5)
            graficos.append(op.plot(fig2, output_type='div', include_plotlyjs=False))

            df_tipo_racao = df.groupby('produto__tipo')['lucro'].sum().reset_index()
            fig3 = px.pie(
                df_tipo_racao,
                names='produto__tipo', 
                values='lucro', 
                title='Proporção de Lucro (Premium vs Normal) - Plataforma', 
                labels={'produto__tipo': 'Tipo de Ração', 'lucro': 'Lucro Total (R$)'}, 
                template='plotly_dark'
            )
            fig3.update_layout(title_x=0.5)
            graficos.append(op.plot(fig3, output_type='div', include_plotlyjs=False))

    else:
        vendas_queryset = Vendas.objects.filter(usuario=user)
        produtos_queryset = Produto.objects.filter(usuario=user)

        vendas_data = list(vendas_queryset.values(
            'produto__nome', 'quantidade_vendida',
            'preco_unitario_venda', 'custo_unitario_venda',
            'produto__tipo', 'produto__animal', 'produto__peso'
        ))

        if not vendas_data:
            graficos.append('<p>Você ainda não registrou nenhuma venda</p>')
            kpis = {
                'Minha Receita': 0, 'Meu Lucro': 0, 'Minhas Vendas': 0,
                'Meus Produtos': produtos_queryset.count()
            }
        else:
            df = pd.DataFrame.from_records(vendas_data)
            df['receita'] = df['quantidade_vendida'] * df['preco_unitario_venda']
            df['lucro'] = df['quantidade_vendida'] * (df['preco_unitario_venda'] - df['custo_unitario_venda'])

            kpis = {
                'Minha Receita': df['receita'].sum(), 'Meu Lucro': df['lucro'].sum(),
                'Minhas Vendas': df.shape[0],
                'Meus Produtos': produtos_queryset.count()
            }

            df_produtos = df.groupby(
                ['produto__animal', 'produto__tipo', 'produto__peso']
            )[['receita', 'lucro']].sum().reset_index()

            def format_peso_kg(p):
                peso_str = f"{p:.2f}".rstrip('0').rstrip('.')
                return f"{peso_str}kg"

            df_produtos['rotulo_produto'] = (
                df_produtos['produto__animal'].str.capitalize() + ' ' +
                df_produtos['produto__tipo'].str.capitalize() + ' (' +
                df_produtos['produto__peso'].apply(format_peso_kg) + ')'
            )

            df_top_produtos = df_produtos.sort_values(by='lucro', ascending=False)
            fig4 = px.bar(
                df_top_produtos,
                x='rotulo_produto',
                y='lucro',
                title='Meu Lucro Total por Produto',
                text='lucro',
                labels={'rotulo_produto': 'Produto', 'lucro': 'Lucro (R$)'},
                template='plotly_dark'
            )

            fig4.update_layout(title_x=0.5)
            fig4.update_traces(texttemplate='R$ %{text:.2f}', textposition='outside')
            graficos.append(op.plot(fig4, output_type='div', include_plotlyjs=False))

            fig5 = px.pie(
                df_produtos,
                names='rotulo_produto',
                values='lucro',
                title='Contribuição de Lucro por Produto',
                labels={'rotulo_produto': 'Produto'},
                template='plotly_dark'
            )

            fig5.update_layout(title_x=0.5)
            graficos.append(op.plot(fig5, output_type='div', include_plotlyjs=False))

            df_tipo_racao_venda = df.groupby('produto__tipo')['lucro'].sum().reset_index()
            fig6 = px.pie(
                df_tipo_racao_venda,
                names='produto__tipo',
                values='lucro',
                title='Minha Proporção de Lucro (Premium vs Normal)',
                labels={'produto__tipo': 'Tipo de Ração', 'lucro': 'Lucro Total (R$)'},
                template='plotly_dark'
            )

            fig6.update_layout(title_x=0.5)
            graficos.append(op.plot(fig6, output_type='div', include_plotlyjs=False))
        
    contexto.update({
        'kpis': kpis,
        'graficos': graficos,
        'produtos': produtos_queryset,
        'vendas': vendas_queryset
    })

    return render(request, 'gestao_pirotech_app/dashboard.html', contexto)
@login_required(login_url='gestao-login')
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
            'catalogo_racoes': catalogo_racoes,
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