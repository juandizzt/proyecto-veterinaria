# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UsuariosRoles
from .forms import CustomUserCreationForm
from .decorators import admin_required, empleado_required, cliente_required, veterinario_required, rol_required
from mascotas.models import Mascota
from citas.models import Cita
from pedidos.models import Pedido
from Productos.models import Producto
from historialM.models import HistorialMedico, Vacuna
# Agrega al inicio del archivo:
from django.utils import timezone

def registro_view(request):
    """
    Vista para registro de nuevos usuarios.
    Por defecto, todos los nuevos usuarios son 'cliente'
    """
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Opcional: Iniciar sesión automáticamente después del registro
            # login(request, user)
            
            messages.success(request, "¡Registro exitoso! Ahora puedes iniciar sesión.")
            return redirect('login')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, "usuarios/registrar.html", {"form": form})

def login_view(request):
    """
    Vista personalizada para login
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f"¡Bienvenido {user.first_name}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    
    return render(request, "usuarios/login.html")

@login_required
def logout_view(request):
    """
    Vista para cerrar sesión
    """
    logout(request)
    messages.success(request, "Sesión cerrada exitosamente")
    return redirect('login')

@login_required
def dashboard_view(request):
    """
    Dashboard principal que redirige según el rol del usuario
    """
    usuario = request.user
    
    if usuario.es_admin():
        return dashboard_admin(request)
    elif usuario.es_empleado():
        return dashboard_empleado(request)
    elif usuario.es_cliente():
        return dashboard_cliente(request)
    elif usuario.es_veterinario():
        return dashboard_veterinario(request)
    else:
        messages.error(request, "Tu cuenta no tiene un rol válido asignado.")
        return redirect('login')

@admin_required
def dashboard_admin(request):
    """
    Dashboard específico para administradores
    """
    context = {
        'total_usuarios': UsuariosRoles.objects.all().count(),
        'total_mascotas': Mascota.objects.all().count(),
        'total_citas': Cita.objects.all().count(),
        'total_pedidos': Pedido.objects.all().count(),
        'total_productos': Producto.objects.all().count(),
        'total_historial_medicos': HistorialMedico.objects.all().count(),
        'total_vacunas': Vacuna.objects.all().count(),
        'usuarios_recientes': UsuariosRoles.objects.all().order_by('-date_joined')[:5],
        'citas_recientes': Cita.objects.all().order_by('-fecha_cita')[:5] if hasattr(Cita, 'fecha_cita') else [],
    }
    return render(request, "usuarios/dashboard_admin.html", context)

@empleado_required
def dashboard_empleado(request):
    """
    Dashboard específico para empleados
    """
    context = {
        'total_citas_hoy': Cita.objects.filter(fecha_cita__date=timezone.now().date()).count(),
        'total_pedidos_pendientes': Pedido.objects.filter(estado='pendiente').count(),
        'productos_bajo_stock': Producto.objects.filter(stock__lt=10)[:5],
        'citas_proximas': Cita.objects.filter(fecha_cita__gte=timezone.now()).order_by('fecha_cita')[:5],
    }
    return render(request, "usuarios/dashboard_empleado.html", context)

@cliente_required
def dashboard_cliente(request):
    """
    Dashboard específico para clientes
    """
    usuario = request.user
    context = {
        'mis_mascotas': Mascota.objects.filter(dueño=usuario),
        'mis_citas': Cita.objects.filter(propietario=usuario).order_by('-fecha_cita')[:5],
        'mis_pedidos': Pedido.objects.filter(usuario=usuario).order_by('-fecha')[:5],
        'citas_proximas': Cita.objects.filter(Cliente=usuario, fecha_cita__gte=timezone.now()).order_by('fecha_cita')[:3],
    }
    return render(request, "usuarios/dashboard_cliente.html", context)

@veterinario_required
def dashboard_veterinario(request):
    """
    Dashboard específico para veterinarios
    """
    context = {
        'citas_hoy': Cita.objects.filter(fecha_cita__date=timezone.now().date()).count(),
        'citas_pendientes': Cita.objects.filter(fecha_cita__gte=timezone.now().date()).count(),
        'mascotas_atendidas': Mascota.objects.all().count(),
        'historiales_recientes': HistorialMedico.objects.all().order_by('-fecha')[:5],
        'citas_programadas': Cita.objects.filter(fecha_cita__gte=timezone.now()).order_by('fecha_cita')[:5],
    }
    return render(request, "usuarios/dashboard_veterinario.html", context)

@admin_required
def lista_usuarios(request):
    """
    Vista para listar todos los usuarios (solo admin)
    """
    usuarios = UsuariosRoles.objects.all().order_by('-date_joined')
    return render(request, "usuarios/lista_usuarios.html", {'usuarios': usuarios})

@admin_required
def cambiar_rol_usuario(request, user_id):
    """
    Vista para cambiar el rol de un usuario (solo admin)
    """
    if request.method == "POST":
        usuario = UsuariosRoles.objects.get(id=user_id)
        nuevo_rol = request.POST.get('rol')
        
        if nuevo_rol in dict(UsuariosRoles.ROLES).keys():
            usuario.rol = nuevo_rol
            usuario.save()
            messages.success(request, f"Rol de {usuario.username} cambiado a {usuario.get_rol_display()}")
        else:
            messages.error(request, "Rol inválido")
    
    return redirect('lista_usuarios')