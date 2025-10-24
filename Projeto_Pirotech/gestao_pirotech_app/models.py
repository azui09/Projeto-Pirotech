from django.db import models
from django.contrib.auth.models import User

catalogo_racoes = {
    'cavalo': {
        'premium': {
            '5kg': {'preco_venda': 80.00, 'preco_custo': 72.00},
            '20kg': {'preco_venda': 280.00, 'preco_custo': 252.00},
        },
        'normal': {
            '5kg': {'preco_venda': 60.00, 'preco_custo': 54.00},
            '20kg': {'preco_venda': 200.00, 'preco_custo': 180.00},
        },
    },
    'bovino': {
        'premium': {
            '10kg': {'preco_venda': 120.00, 'preco_custo': 108.00},
            '25kg': {'preco_venda': 280.00, 'preco_custo': 252.00},
        },
        'normal': {
            '10kg': {'preco_venda': 90.00, 'preco_custo': 81.00},
            '25kg': {'preco_venda': 200.00, 'preco_custo': 180.00},
        },
    },
    'ovelha': {
        'premium': {
            '2kg': {'preco_venda': 25.00, 'preco_custo': 22.50},
            '5kg': {'preco_venda': 55.00, 'preco_custo': 49.50},
        },
        'normal': {
            '2kg': {'preco_venda': 18.00, 'preco_custo': 16.20},
            '5kg': {'preco_venda': 40.00, 'preco_custo': 36.00},
        },
    },
    'porco': {
        'premium': {
            '1kg': {'preco_venda': 12.00, 'preco_custo': 10.80},
            '5kg': {'preco_venda': 55.00, 'preco_custo': 49.50},
        },
        'normal': {
            '1kg': {'preco_venda': 8.00, 'preco_custo': 7.20},
            '5kg': {'preco_venda': 40.00, 'preco_custo': 36.00},
        },
    },
    'galinha': {
        'premium': {
            '0.5kg': {'preco_venda': 10.00, 'preco_custo': 9.00},
            '1kg': {'preco_venda': 18.00, 'preco_custo': 16.20},
        },
        'normal': {
            '0.5kg': {'preco_venda': 7.00, 'preco_custo': 6.30},
            '1kg': {'preco_venda': 14.00, 'preco_custo': 12.60},
        },
    },
}

class Usuarios(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    cargo = models.CharField(max_length=10, choices=ROLE_CHOICES, default='vendedor')

    def __str__(self):
        return f"{self.user.username} ({self.cargo})"
    
class Produto(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    animal = models.CharField(max_length=50)
    tipo = models.CharField(max_length=50)
    peso = models.DecimalField(max_digits=4, decimal_places=2)
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    preco_de_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantidade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nome} - {self.usuario.username}"
    
class Vendas(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    quantidade_vendida = models.PositiveIntegerField()
    preco_unitario_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    custo_unitario_venda = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    @property
    def receita_total(self):
        return self.quantidade_vendida * self.preco_unitario_venda

    @property
    def lucro_total(self):
        return self.quantidade_vendida * (self.preco_unitario_venda - self.custo_unitario_venda)

    def __str__(self):
        return f"{self.produto.nome} ({self.quantidade_vendida} un) - {self.usuario.username}"