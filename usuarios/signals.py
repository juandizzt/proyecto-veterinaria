from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Permission

@receiver(post_migrate)
def crear_grupos(sender, **kwargs):
    grupos = {
        "admin": [],
        "empleado": [],
        "usuario": [],
    }

    admin = Group.objects.get_or_create(name="admin")[0]
    empleado = Group.objects.get_or_create(name="empleado")[0]
    usuario = Group.objects.get_or_create(name="usuario")[0]

    # Solo admin puede ver historial de citas
    permiso_historial = Permission.objects.get(codename="view_cita")
    admin.permissions.add(permiso_historial)

    # Empleado puede ver mascotas y citas, pero no historial global
    permiso_mascota = Permission.objects.get(codename="view_mascota")
    permiso_cita = Permission.objects.get(codename="view_cita")
    empleado.permissions.add(permiso_mascota, permiso_cita)

    # Usuario solo puede ver lo suyo (esto se controla en la vista)

