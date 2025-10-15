from django.urls import path
from . import views

urlpatterns = [
    path('', views.cadastro, name='gestao-cadastro'),
    path('login/', views.login, name='gestao-login'),
    #path('dashboard/', views.dashboard, name='gestao-dashboard'),
    #path('logout/', views.fazer_logout, name='gestao-logout'),
]