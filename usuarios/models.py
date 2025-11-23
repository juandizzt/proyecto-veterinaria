from django.db import models


class Usuario(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    email = models.EmailField(verbose_name="Correo Electronico")
    password = models.CharField(max_length=100, verbose_name="Contraseña")

    def __str__(self):
        return self.nombre
