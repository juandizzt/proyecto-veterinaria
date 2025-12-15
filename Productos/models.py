from django.db import models

class Producto(models.Model):
    codigo = models.AutoField(primary_key=True, verbose_name="Código del producto")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del producto")
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Precio del producto"
    )
    descripcion = models.TextField(
        max_length=300, verbose_name="Descripcion del producto"
    )
    stock = models.IntegerField(verbose_name="Cantidad")
    imagen = models.ImageField(
        upload_to="productos/",
        null=True,
        blank=True,
        verbose_name="Imagen del producto",
    )

    def __str__(self):
        return self.nombre