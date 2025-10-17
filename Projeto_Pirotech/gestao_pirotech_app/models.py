from django.db import models
from django.contrib.auth.models import User

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
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nome} - {self.usuario.username}"
    
class Vendas(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    quantidade_vendida = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.produto.nome} ({self.quantidade_vendida} un) - {self.usuario.username}"