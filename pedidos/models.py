# pedidos/models.py
from django.db import models
from django.conf import settings
from Productos.models import Producto


class Pedido(models.Model):
    ESTADOS = [
        ('PENDIENTE',   'Pendiente'),
        ('CONFIRMADO',  'Confirmado'),   # ← cliente presionó "Proceder al Pago"
        ('PAGADO',      'Pagado'),
        ('ENVIADO',     'Enviado'),
        ('CANCELADO',   'Cancelado'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    fecha   = models.DateTimeField(auto_now_add=True)
    estado  = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    total   = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username} [{self.estado}]"

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-fecha']   # más recientes primero


class DetallePedido(models.Model):
    pedido   = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def save(self, *args, **kwargs):
        if self.producto:
            self.subtotal = self.producto.precio * self.cantidad
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Detalle de Pedido"
        verbose_name_plural = "Detalles de Pedido"