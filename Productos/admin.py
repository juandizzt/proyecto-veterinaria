from django.contrib import admin
from .models import Producto


class ProductAdmin(admin.ModelAdmin):
    list_display = ["nombre", "precio"]  # Cambiar "lista_display" por "list_display"
    search_fields = ["nombre"]


admin.site.register(Producto, ProductAdmin)
