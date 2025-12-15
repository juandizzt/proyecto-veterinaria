from django.db import models
from django.contrib.auth.models import AbstractUser

class UsuariosRoles(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('empleado', 'Empleado'),
        ('cliente', 'Cliente'),
        ('veterinario', 'Veterinario'),
    )

    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.CharField(max_length=255, blank=True)  # ¡CORREGIDO!
    fecha_registro = models.DateTimeField(auto_now_add=True)  # Corregí "feca_registro"

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} ({self.get_rol_display()})"
    
    def es_admin(self):
        return self.rol == 'admin'
    
    def es_empleado(self):
        return self.rol == 'empleado'
    
    def es_cliente(self):
        return self.rol == 'cliente'
    
    def es_veterinario(self):
        return self.rol == 'veterinario'