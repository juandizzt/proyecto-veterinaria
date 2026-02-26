# usuarios/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UsuariosRoles
from django.utils.translation import gettext_lazy as _

class CustomUserAdmin(UserAdmin):
    # Configuración para la lista de usuarios
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff', 'is_active', 'fecha_registro')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'telefono')
    ordering = ('-fecha_registro',)
    
    # Campos para mostrar en el formulario de edición
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Información personal'), {'fields': ('first_name', 'last_name', 'email', 'telefono', 'direccion')}),
        (_('Roles y permisos'), {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Fechas importantes'), {'fields': ('last_login', 'date_joined', 'fecha_registro')}),
    )
    
    # Campos para el formulario de creación
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'rol', 'telefono', 'direccion'),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ('last_login', 'date_joined', 'fecha_registro')

# Registra el modelo en el admin
admin.site.register(UsuariosRoles, CustomUserAdmin)