from django.contrib import admin
from .models import Pedido, PedidoProducto


# Register your models here.
class PedidoproductoInlineAdmin(admin.TabularInline):
    model = PedidoProducto
    extra = 0


class PedidoAdmin(admin.ModelAdmin):
    model = Pedido
    inlines = [PedidoproductoInlineAdmin]


admin.site.register(Pedido, PedidoAdmin)
