# usuarios/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from .models import UsuariosRoles

@receiver(post_save, sender=UsuariosRoles)
def asignar_rol_por_defecto(sender, instance, created, **kwargs):
    """
    Asigna permisos y grupos según el rol cuando se crea un usuario.
    """
    if created:
        # Por defecto, todos los nuevos usuarios son 'cliente'
        if not instance.rol:
            instance.rol = 'cliente'
            instance.save()
        
        # Asignar al grupo correspondiente
        try:
            grupo, _ = Group.objects.get_or_create(name=instance.rol)
            instance.groups.add(grupo)
        except Group.DoesNotExist:
            # Si el grupo no existe, lo creamos
            grupo = Group.objects.create(name=instance.rol)
            instance.groups.add(grupo)
        
        print(f"✅ Usuario {instance.username} asignado al grupo '{instance.rol}'")

@receiver(post_save, sender=UsuariosRoles)
def configurar_superusuario(sender, instance, **kwargs):
    """
    Asegura que los superusuarios tengan rol 'admin'
    """
    if instance.is_superuser and instance.rol != 'admin':
        instance.rol = 'admin'
        instance.save(update_fields=['rol'])