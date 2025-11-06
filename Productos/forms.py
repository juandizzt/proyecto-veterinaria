from django import forms
from .models import Producto
from django.db import models


class ProductForm(forms.Form):
    nombre = forms.CharField(max_length=200, label="Nombre")
    precio = forms.DecimalField(max_digits=10, decimal_places=2, label="Precio")
    descripcion = forms.CharField(max_length=300, label="Descripción")
    stock = models.IntegerField(verbose_name="Cantidad")
    imagen = models.ImageField(
        upload_to="productos/",
        null=True,
        blank=True,
        verbose_name="Imagen del producto",
    )

    def save(self):
        Producto.objects.create(
            codigo=self.cleaned_data["codigo"],
            nombre=self.cleaned_data["Nombre"],
            precio=self.cleaned_data["precio"],
            descripcion=self.cleaned_data["descripcion"],
            stock=self.cleaned_data["stock"],
            imagen=self.cleaned_data["imagen"],
            id=self.cleaned_data["id"],
        )
