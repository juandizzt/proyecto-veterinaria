from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime


class Cita(models.Model):
    TIPO_SERVICIO_CHOICES = [
        ("consulta", "Consulta General"),
        ("vacunacion", "Vacunación"),
        ("estetica", "Estética"),
        ("urgencia", "Urgencia"),
        ("cirugia", "Cirugía"),
    ]

    mascota = models.CharField(max_length=100, verbose_name="Nombre de la Mascota")
    propietario = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Propietario"
    )
    tipo_mascota = models.CharField(max_length=50, verbose_name="Tipo de Mascota")
    tipo_servicio = models.CharField(
        max_length=20, choices=TIPO_SERVICIO_CHOICES, default="consulta"
    )
    fecha_cita = models.DateField(verbose_name="Fecha de la cita")
    hora_cita = models.TimeField(verbose_name="Hora de la cita")
    descripcion = models.TextField(verbose_name="Descripción del problema", blank=True)
    telefono = models.CharField(max_length=15, verbose_name="Teléfono de contacto")
    email = models.EmailField(verbose_name="Correo electrónico")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    @property
    def es_pasada(self):
        """Verifica si la cita ya pasó"""
        hoy = timezone.now().date()
        ahora = timezone.now().time()

        if self.fecha_cita < hoy:
            return True
        elif self.fecha_cita == hoy and self.hora_cita < ahora:
            return True
        return False

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ["fecha_cita", "hora_cita"]

    def __str__(self):
        return f"{self.mascota} - {self.fecha_cita} {self.hora_cita}"
