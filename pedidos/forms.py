from django.forms import ModelForm
from .models import PedidoProducto

class PedidoProductoForm(ModelForm):
    class Meta:
        model = PedidoProducto
        fields = ['producto', 'cantidad']