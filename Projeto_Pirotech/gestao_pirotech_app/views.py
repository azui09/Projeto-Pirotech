from django.shortcuts import render

def cadastro(request):
    return render(request, 'gestao_pirotech_app/cadastro.html')