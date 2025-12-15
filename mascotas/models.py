from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Mascota(models.Model):
    dueño = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mascotas'
    )
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=100, blank=True, null=True)
    edad = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} ({self.especie})"
