from django import forms
from .models import Producto


class ProductForm(forms.Form):
    nombre = forms.CharField(max_length=200, label="Nombre")
    precio = forms.DecimalField(max_digits=10, decimal_places=2, label="Precio")
    descripcion = forms.CharField(
        widget=forms.Textarea, max_length=300, label="Descripción"
    )
    stock = forms.IntegerField(label="Cantidad")
    imagen = forms.ImageField(
        required=False, label="Imagen del producto"  # En lugar de null=True, blank=True
    )

    def save(self):
        # Crear producto sin codigo e id (se generan automáticamente)
        Producto.objects.create(
            nombre=self.cleaned_data["nombre"],  # Cambiar "Nombre" por "nombre"
            precio=self.cleaned_data["precio"],
            descripcion=self.cleaned_data["descripcion"],
            stock=self.cleaned_data["stock"],
            imagen=self.cleaned_data["imagen"],
        )
