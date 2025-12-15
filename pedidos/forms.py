from django import forms
from .models import DetallePedido

class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ['producto', 'cantidad']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'}),
            'producto': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'producto': 'Producto',
            'cantidad': 'Cantidad',
        }