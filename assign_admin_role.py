# assign_admin_role.py
import os
import django
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProyectoV.settings')
django.setup()

from usuarios.models import UsuariosRoles

def assign_admin_role():
    """Asigna rol 'admin' al superusuario"""
    try:
        # Buscar el superusuario (normalmente se llama 'admin')
        admin_user = UsuariosRoles.objects.get(username='admin')
        
        # Configurar como administrador
        admin_user.rol = 'admin'
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        print("=" * 50)
        print("✅ CONFIGURACIÓN EXITOSA")
        print("=" * 50)
        print(f"Usuario: {admin_user.username}")
        print(f"Rol asignado: {admin_user.rol}")
        print(f"Es staff: {admin_user.is_staff}")
        print(f"Es superusuario: {admin_user.is_superuser}")
        print("=" * 50)
        print("\n🎯 Ahora puedes iniciar sesión con:")
        print("   Usuario: admin")
        print("   Contraseña: La que creaste anteriormente")
        
    except UsuariosRoles.DoesNotExist:
        print("❌ ERROR: Usuario 'admin' no encontrado.")
        print("\n📝 EJECUTA PRIMERO:")
        print("1. python manage.py makemigrations")
        print("2. python manage.py migrate")
        print("3. python manage.py createsuperuser")
        print("\nDurante la creación ingresa:")
        print("   Username: admin")
        print("   Email: admin@veterinaria.com")
        print("   Password: Admin123! (o el que prefieras)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        sys.exit(1)

if __name__ == "__main__":
    assign_admin_role()