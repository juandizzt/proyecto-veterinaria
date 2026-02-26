# mascotas/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class Mascota(models.Model):
    # Relación con el usuario personalizado
    dueño = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mascotas'
    )
    nombre = models.CharField(max_length=100)
    especie = models.CharField(max_length=50)
    raza = models.CharField(max_length=100, blank=True, null=True)
    
    # Edad y Peso configurados para decimales como se ve en tu diseño
    edad = models.DecimalField(
        max_digits=4, 
        decimal_places=1, 
        default=0,
        help_text="Edad en años (ej: 2.5)"
    )
    
    peso = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True,
        help_text="Peso en kg (ej: 5.25)"
    )
    
    # Campo para las notas que aparecen en el formulario púrpura
    observaciones = models.TextField(blank=True, null=True)
    
    # Campo para la foto (requiere Pillow instalado: pip install Pillow)
    foto = models.ImageField(upload_to='mascotas_fotos/', blank=True, null=True)
    
    fecha_registro = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.nombre} ({self.especie}) - {self.dueño.username}"
    
    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Mascota'
        verbose_name_plural = 'Mascotas'