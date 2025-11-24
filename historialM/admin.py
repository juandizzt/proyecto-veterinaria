from django.contrib import admin
from django.contrib.auth.models import Group
from .models import HistorialMedico, Vacuna

# Register your models here.

class VacunaInline(admin.TabularInline):
    model = Vacuna
    extra = 1

@admin.register(HistorialMedico)
class HistorialMedicoAdmin(admin.ModelAdmin):
    list_display = [
        'mascota', 
        'propietario', 
        'tipo_consulta', 
        'fecha_consulta', 
        'veterinario', 
        'estado_salud',
        'es_urgente'
    ]
    list_filter = [
        'tipo_consulta', 
        'fecha_consulta', 
        'estado_salud', 
        'es_urgente',
        'veterinario'
    ]
    search_fields = [
        'mascota', 
        'propietario__username', 
        'diagnostico', 
        'tratamiento'
    ]
    readonly_fields = ['creado_en', 'actualizado_en']
    inlines = [VacunaInline]
    
    # Restringir acceso solo a veterinarios y superusuarios
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filtrar solo los historiales donde el usuario es el veterinario
        return qs.filter(veterinario=request.user)

    def has_module_permission(self, request):
        # Solo superusuarios y veterinarios pueden ver el módulo
        return (request.user.is_superuser or 
                request.user.groups.filter(name='Veterinarios').exists())

@admin.register(Vacuna)
class VacunaAdmin(admin.ModelAdmin):
    list_display = ['nombre_vacuna', 'historial', 'fecha_aplicacion', 'veterinario_aplico']
    list_filter = ['fecha_aplicacion', 'nombre_vacuna']

# Crear grupo de Veterinarios si no existe
try:
    veterinarios_group, created = Group.objects.get_or_create(name='Veterinarios')
except:
    pass