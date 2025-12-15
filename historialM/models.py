from django.db import models
from django.contrib.auth.models import User
from citas.models import Cita
from django.core.exceptions import PermissionDenied
from django.conf import settings
#Permissionsdenied importa una exceptions para denegar el acceso programaticamente
# Create your models here.

class HistorialMedico(models.Model):
    TIPO_CONSULTA_CHOICHES = [
        ("consulta", "Consulta General"),
        ("vacunacion", "Vacunación"),
        ("estetica", "Estética"),
        ("urgencia", "Urgencia"),
        ("cirugia", "Cirugía"),
        ("control", "Control"),
        ("emergencia", "Emergencia"),
    ]

    ESTADO_SALUD_CHOICES = [
        ("excelente", "Excelente"),
        ("bueno", "Bueno"),
        ("regular", "Regular"),
        ("grave", "Grave"),
        ("critico", "Crítico"),
    ]

    #relaciono la mascota a traves de la cita y el propietario

    cita = models.ForeignKey(
        Cita,
        on_delete=models.CASCADE,
        verbose_name="Cita relacionada"
    )
    mascota = models.CharField(max_length=100, verbose_name="Nombre de la Mascota")
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='historiales_propietario'
    )
    veterinario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='historiales_veterinario'
    )
    fecha_consulta = models.DateField(verbose_name="Fecha de consulta")
    tipo_consulta = models.CharField(
        max_length=20,
        choices=TIPO_CONSULTA_CHOICHES,
        verbose_name="Tipo de consulta"
    )
    diagnostico = models.TextField(verbose_name="Diagnostico")
    tratamiento = models.TextField(verbose_name="Tratamiento prescrito")
    medicamentos = models.TextField(
        verbose_name="Medicamentos administrados",
        blank=True #si no se ingresa nada se muestra vacio si es falso el campo es obligatorio
    )
    observaciones = models.TextField(
        verbose_name="Observaciones adicionales",
        blank=True
    )
    peso = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="Peso (Kg)",
        null=True,
        blank=True
    )
    temperatura = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        verbose_name="Temperatura (°C)", 
        null=True, 
        blank=True
    )
    estado_salud = models.CharField(
        max_length=20, 
        choices=ESTADO_SALUD_CHOICES, 
        default="bueno",
        verbose_name="Estado de salud"
    )

    #campos de control

    proxima_cita = models.DateField(
        verbose_name="Proxima cita recomendada",
        null=True,
        blank=True 
    )
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    es_urgente = models.BooleanField(default=False, verbose_name="Caso urgente")

    class Meta:
        verbose_name = "Historial Médico"
        verbose_name_plural = "Historiales Médicos"
        ordering = ["-fecha_consulta", "-creado_en"]
        permissions = [
            ("puede_ver_historial", "Puede ver historiales médicos"),
            ("puede_editar_historial", "Puede editar historiales médicos"),
        ]

    def __str__(self):
        return f"Historial de {self.mascota} - {self.fecha_consulta}"

    def save(self, *args, **kwargs):
        # Si se crea desde una cita, copiar información básica
        if self.cita and not self.mascota:
            self.mascota = self.cita.mascota
            self.propietario = self.cita.propietario
            self.tipo_mascota = self.cita.tipo_mascota
            self.fecha_consulta = self.cita.fecha_cita
        super().save(*args, **kwargs)

    @property
    def tiene_proxima_cita(self):
        return self.proxima_cita is not None

class Vacuna(models.Model):
    historial = models.ForeignKey(
        HistorialMedico, 
        on_delete=models.CASCADE, 
        related_name="vacunas"
    )
    nombre_vacuna = models.CharField(max_length=100, verbose_name="Nombre de la vacuna")
    fecha_aplicacion = models.DateField(verbose_name="Fecha de aplicación")
    proxima_dosis = models.DateField(
        verbose_name="Próxima dosis", 
        null=True, 
        blank=True
    )
    lote = models.CharField(max_length=50, verbose_name="Número de lote", blank=True)
    veterinario_aplico = models.CharField(
        max_length=100, 
        verbose_name="Veterinario que aplicó"
    )

    class Meta:
        verbose_name = "Vacuna"
        verbose_name_plural = "Vacunas"

    def __str__(self):
        return f"{self.nombre_vacuna} - {self.fecha_aplicacion}"