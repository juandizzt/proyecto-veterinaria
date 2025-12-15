# pedidos/admin.py - VERSIÓN SIMPLE
from django.contrib import admin
from .models import Pedido, DetallePedido

# Inline para mostrar detalles dentro del pedido
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    inlines = [DetallePedidoInline]
    list_display = ['id', 'usuario', 'fecha', 'estado', 'total']
    list_filter = ['estado', 'fecha']
    search_fields = ['usuario__username']


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'pedido', 'producto', 'cantidad', 'subtotal']
    list_filter = ['pedido__estado']
    search_fields = ['producto__nombre']