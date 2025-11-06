from django.contrib import admin
from .models import Producto


# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    model = Producto
    lista_display = ("nombre", "precio")
    search_fields = "nombre"


admin.site.register(Producto, ProductAdmin)
