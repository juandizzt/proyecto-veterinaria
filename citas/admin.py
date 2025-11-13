from django.contrib import admin
from .models import Cita

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ['mascota', 'propietario', 'tipo_servicio', 'fecha_cita', 'hora_cita', 'telefono']
    list_filter = ['tipo_servicio', 'fecha_cita', 'tipo_mascota']
    search_fields = ['mascota', 'propietario__username', 'telefono', 'email']
    date_hierarchy = 'fecha_cita'
    ordering = ['-fecha_cita', '-hora_cita']