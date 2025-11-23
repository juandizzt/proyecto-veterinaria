from django.db import models
from django.contrib.auth.models import User
from Productos.models import Producto


class Pedido(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    pedido_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"order {self.id} by {self.usuario}"

    @property
    def total(self):
        return sum(item.subtotal for item in self.pedidoproducto_set.all())

class PedidoProducto(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()

    def __str__(self) -> str:
        return f"{self.pedido} pedido {self.producto}"
    
    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad

# Create your models here.
