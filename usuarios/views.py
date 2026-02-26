# usuarios/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from .models import UsuariosRoles, PasswordReset
from .forms import CustomUserCreationForm
from .decorators import admin_required, empleado_required, cliente_required, veterinario_required, rol_required
from mascotas.models import Mascota
from citas.models import Cita
from pedidos.models import Pedido
from Productos.models import Producto
from historialM.models import HistorialMedico, Vacuna
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .serializers import ResetPasswordSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import send_mail

from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.urls import reverse_lazy



import os

User = get_user_model()


# ─── Vista personalizada: redirige al mismo form con ?sent=1 para mostrar modal ───

class CustomPasswordResetView(PasswordResetView):
    template_name = 'usuarios/recuperar_password.html'
    email_template_name = 'usuarios/password_reset_email.html'
    subject_template_name = 'usuarios/password_reset_subject.txt'
    # ❌ NO pongas success_url aquí con reverse_lazy + string

    def get_success_url(self):
        from django.urls import reverse
        return reverse('recuperar_password') + '?sent=1'


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'usuarios/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'usuarios/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'usuarios/password_reset_complete.html'

# ─────────────────────────────────────────────
# SISTEMA 2 — DRF API views (para frontend SPA)
# ─────────────────────────────────────────────

class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.RegexField(
        regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
        write_only=True,
        error_messages={
            'invalid': 'La contraseña debe tener mínimo 8 caracteres, una mayúscula, un número y un carácter especial.'
        }
    )
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Las contraseñas no coinciden.'})
        return attrs


class RequestPasswordReset(generics.GenericAPIView):
    """
    POST /reset-password/
    Body: { "email": "usuario@ejemplo.com" }
    Envía un email con el link para restablecer la contraseña.
    """
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer  # solo se usa para documentación, la lógica es manual

    def post(self, request):
        email = request.data.get('email', '').strip()
        if not email:
            return Response({'error': 'Email requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(email__iexact=email).first()

        if user:
            token_generator = PasswordResetTokenGenerator()
            token = token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            base_url = os.environ.get('PASSWORD_RESET_BASE_URL', 'http://localhost:8000')
            reset_url = f"{base_url}/usuarios/reset-password-confirm/{uid}/{token}/"

            message = render_to_string('usuarios/password_reset_email.html', {
                'user': user,
                'reset_url': reset_url,
            })
            send_mail(
                subject='Restablece tu contraseña',
                message='',
                from_email='noreply@tudominio.com',
                recipient_list=[user.email],
                html_message=message,
            )

        # Siempre responde igual por seguridad (no revelar si el email existe)
        return Response(
            {'success': 'Si el email existe, recibirás un enlace para restablecer la contraseña.'},
            status=status.HTTP_200_OK
        )


class PasswordResetConfirm(generics.GenericAPIView):
    """
    POST /reset-password-confirm/<uidb64>/<token>/
    Body: { "new_password": "...", "confirm_password": "..." }
    """
    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'error': 'Enlace inválido.'}, status=status.HTTP_400_BAD_REQUEST)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({'error': 'Token inválido o expirado.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'success': 'Contraseña restablecida correctamente.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        return redirect('dashboard')  # ✅ Correcto
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # ✅ Si el first_name no está en Title Case, corregirlo
            if user.first_name and user.first_name != user.first_name.title():
                user.first_name = user.first_name.strip().title()
                user.save(update_fields=['first_name'])
            login(request, user)
            nombre_mostrar = user.first_name if user.first_name else user.username
            messages.success(request, f"¡Bienvenido {nombre_mostrar}!")
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
    Dashboard específico para administradores con información detallada
    """
    try:
        # Obtener todas las citas recientes - NO usar select_related con 'mascota' porque es CharField
        citas_recientes = Cita.objects.all().order_by('-fecha_cita', '-hora_cita')[:10]
        
        # Obtener todos los pedidos recientes
        pedidos_recientes = Pedido.objects.all().order_by('-fecha')[:10]
        
        # Obtener todas las mascotas con detalles
        mascotas_registradas = Mascota.objects.all().order_by('-id')[:10]
        
        # Obtener citas de hoy
        hoy = timezone.now().date()
        citas_hoy_count = Cita.objects.filter(fecha_cita=hoy).count()
        
        # Productos con bajo stock
        productos_bajo_stock = []

        pedidos_recientes = Pedido.objects.filter(
            estado__in=['CONFIRMADO', 'PAGADO', 'ENVIADO', 'CANCELADO']
        ).order_by('-fecha')[:10]

        total_pedidos = Pedido.objects.filter(
            estado__in=['CONFIRMADO', 'PAGADO', 'ENVIADO', 'CANCELADO']
        ).count()

        pedidos_pendientes_count = Pedido.objects.filter(estado='PENDIENTE').count()

        try:
            productos_bajo_stock = Producto.objects.filter(stock__lt=5)[:5]
        except:
            pass
        
    except Exception as e:
        print(f"Error en dashboard_admin: {e}")
        # Valores por defecto en caso de error
        citas_recientes = []
        pedidos_recientes = []
        mascotas_registradas = []
        citas_hoy_count = 0
        productos_bajo_stock = []
    
    context = {
        'total_usuarios': UsuariosRoles.objects.all().count(),
        'total_mascotas': Mascota.objects.all().count(),
        'total_citas': Cita.objects.all().count(),
        'total_pedidos': total_pedidos,
        'total_productos': Producto.objects.all().count() if hasattr(Producto, 'objects') else 0,
        'usuarios_recientes': UsuariosRoles.objects.all().order_by('-date_joined')[:10],
        'citas_recientes': citas_recientes,
        'pedidos_recientes': pedidos_recientes,
        'mascotas_registradas': mascotas_registradas,
        'productos_bajo_stock': productos_bajo_stock,
        'citas_hoy': citas_hoy_count,
        'pedidos_pendientes': pedidos_pendientes_count,
    }
    return render(request, "usuarios/dashboard_admin.html", context)

@empleado_required
def dashboard_empleado(request):
    """
    Dashboard específico para empleados
    """
    try:
        hoy = timezone.now().date()
        total_citas_hoy = Cita.objects.filter(fecha_cita=hoy).count()
        total_pedidos_pendientes = Pedido.objects.filter(estado='PENDIENTE').count()
        citas = Cita.objects.filter(estado='pendiente')  # Ajusta filtro
        
        # Productos bajo stock
        productos_bajo_stock = []
        try:
            productos_bajo_stock = Producto.objects.filter(stock__lt=10)[:5]
        except:
            pass
        
        # Citas próximas
        citas_proximas = Cita.objects.filter(fecha_cita__gte=hoy).order_by('fecha_cita', 'hora_cita')[:5]
        
        # Citas de hoy
        citas_hoy = Cita.objects.filter(fecha_cita=hoy).order_by('hora_cita')
        
    except Exception as e:
        print(f"Error en dashboard_empleado: {e}")
        total_citas_hoy = 0
        total_pedidos_pendientes = 0
        productos_bajo_stock = []
        citas_proximas = []
        citas_hoy = []
    
    context = {
        'total_citas_hoy': total_citas_hoy,
        'total_pedidos_pendientes': total_pedidos_pendientes,
        'productos_bajo_stock': productos_bajo_stock,
        'citas_proximas': citas_proximas,
        'citas_hoy': citas_hoy,
        'citas': citas,
    }
    return render(request, "usuarios/dashboard_empleado.html", context)

@cliente_required
def dashboard_cliente(request):
    """
    Dashboard específico para clientes
    """
    usuario = request.user
    
    try:
        mis_mascotas = Mascota.objects.filter(dueño=usuario)
        mis_citas = Cita.objects.filter(propietario=usuario).order_by('-fecha_cita', '-hora_cita')[:5]
        
        # Pedidos del cliente
        mis_pedidos = []
        try:
            mis_pedidos = Pedido.objects.filter(usuario=usuario).order_by('-fecha')[:5]
        except:
            pass
        
        # Citas próximas del cliente
        hoy = timezone.now().date()
        citas_proximas = Cita.objects.filter(propietario=usuario, fecha_cita__gte=hoy).order_by('fecha_cita', 'hora_cita')[:3]
        
    except Exception as e:
        print(f"Error en dashboard_cliente: {e}")
        mis_mascotas = []
        mis_citas = []
        mis_pedidos = []
        citas_proximas = []
    
    context = {
        'mis_mascotas': mis_mascotas,
        'mis_citas': mis_citas,
        'mis_pedidos': mis_pedidos,
        'citas_proximas': citas_proximas,
    }
    return render(request, "usuarios/dashboard_cliente.html", context)

# NUEVA VERSIÓN COMPLETA DE dashboard_veterinario
@veterinario_required
def dashboard_veterinario(request):
    """
    Dashboard específico para veterinarios - VERSIÓN COMPLETA
    """
    User = get_user_model()

    if not request.user.groups.filter(name='veterinario').exists() and not request.user.es_veterinario():
        return redirect('dashboard_cliente')

    try:
        hoy = date.today()

        # 1. Citas del día
        citas_hoy_list = Cita.objects.filter(fecha_cita=hoy).order_by('hora_cita')

        # 2. Próximas citas (próximos 7 días)
        citas_programadas = Cita.objects.filter(
            fecha_cita__gte=hoy,
            fecha_cita__lte=hoy + timedelta(days=7)
        ).order_by('fecha_cita', 'hora_cita')[:10]

        # 3. Historiales recientes (últimos 10) ✅ CORREGIDO: '-fecha_consulta'
        historiales_recientes = []
        try:
            historiales_recientes = HistorialMedico.objects.order_by('-fecha_consulta')[:10]
        except:
            pass

        # 4. Obtener clientes
        try:
            grupo_cliente = Group.objects.get(name='cliente')
            clientes = grupo_cliente.user_set.all().order_by('-date_joined')
        except Group.DoesNotExist:
            clientes = User.objects.none()

        # 5. Estadísticas
        citas_hoy_count = citas_hoy_list.count()
        citas_pendientes_count = Cita.objects.filter(fecha_cita__gte=hoy).count()
        mascotas_atendidas = Mascota.objects.count()
        mascotas = Mascota.objects.all()  # ✅ todas las mascotas para el select

        total_clientes = clientes.count()

    except Exception as e:
        print(f"Error en dashboard_veterinario: {e}")
        messages.error(request, f"Error al cargar datos: {str(e)}")

        citas_hoy_list = []
        citas_programadas = []
        historiales_recientes = []
        clientes = []
        citas_hoy_count = 0
        citas_pendientes_count = 0
        mascotas_atendidas = 0
        total_clientes = 0
        mascotas = []  # ✅ AGREGADO: evita error en el contexto si falla el try

    context = {
        'citas_hoy': citas_hoy_count,
        'citas_pendientes': citas_pendientes_count,
        'mascotas_atendidas': mascotas_atendidas,
        'citas_hoy_list': citas_hoy_list,
        'citas_programadas': citas_programadas,
        'historiales_recientes': historiales_recientes,
        'clientes': clientes,
        'total_clientes': total_clientes,
        'mascotas': mascotas,
    }
    return render(request, "usuarios/dashboard_veterinario.html", context)
# NUEVA FUNCIÓN: Registrar mascota
@login_required
def registrar_mascota(request):
    """
    Vista para registrar una nueva mascota (para veterinarios)
    """
    User = get_user_model()
    # Verificar que sea veterinario
    if not request.user.groups.filter(name='veterinario').exists() and not request.user.es_veterinario():
        messages.error(request, "No tienes permiso para registrar mascotas")
        return redirect('dashboard_cliente')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            dueño_id = request.POST.get('dueño')
            especie = request.POST.get('especie')
            raza = request.POST.get('raza')
            edad = request.POST.get('edad')
            peso = request.POST.get('peso')
            observaciones = request.POST.get('observaciones')
            foto = request.FILES.get('foto')
            
            # Validaciones básicas
            if not nombre or not dueño_id or not especie or not edad:
                messages.error(request, "Por favor completa todos los campos obligatorios")
                return redirect('dashboard_veterinario')
            
            # Obtener el dueño
            try:
                dueño = User.objects.get(id=dueño_id)
            except User.DoesNotExist:
                messages.error(request, "El dueño seleccionado no existe")
                return redirect('dashboard_veterinario')
            
            # Crear la mascota
            mascota = Mascota.objects.create(
                nombre=nombre,
                dueño=dueño,
                especie=especie,
                raza=raza if raza else None,
                edad=float(edad) if edad else 0,
                peso=float(peso) if peso else None,
                observaciones=observaciones,
                foto=foto,
            )
            
            messages.success(request, f"Mascota '{nombre}' registrada exitosamente")
            
        except ValueError as e:
            print(f"Error de valor al registrar mascota: {e}")
            messages.error(request, "Error en los datos ingresados. Verifica la edad y el peso.")
        except Exception as e:
            print(f"Error al registrar mascota: {e}")
            messages.error(request, f"Error al registrar mascota: {str(e)}")
        
        return redirect('dashboard_veterinario')
    
    # Si es GET, redirigir al dashboard
    return redirect('dashboard_veterinario')

# NUEVA FUNCIÓN: Agregar producto (para administradores)
@login_required
def agregar_producto(request):
    """
    Vista para agregar un nuevo producto (para administradores)
    """
    # Verificar que sea administrador
    if not request.user.is_superuser and not request.user.es_admin():
        messages.error(request, "No tienes permiso para agregar productos")
        return redirect('dashboard_cliente')
    
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            nombre = request.POST.get('nombre')
            precio = request.POST.get('precio')
            descripcion = request.POST.get('descripcion')
            stock = request.POST.get('stock')
            imagen = request.FILES.get('imagen')
            
            # Validaciones
            if not nombre or not precio or not descripcion or not stock:
                messages.error(request, "Por favor completa todos los campos obligatorios")
                return redirect('dashboard_admin')
            
            # Crear el producto
            producto = Producto.objects.create(
                nombre=nombre,
                precio=float(precio),
                descripcion=descripcion,
                stock=int(stock),
                imagen=imagen,
            )
            
            messages.success(request, f"Producto '{nombre}' agregado exitosamente")
            
        except ValueError as e:
            print(f"Error de valor al agregar producto: {e}")
            messages.error(request, "Error en los datos ingresados. Verifica el precio y el stock.")
        except Exception as e:
            print(f"Error al agregar producto: {e}")
            messages.error(request, f"Error al agregar producto: {str(e)}")
        
        return redirect('dashboard_admin')
    
    # Si es GET, mostrar formulario en el dashboard admin
    return redirect('dashboard_admin')

# NUEVA FUNCIÓN: Detalle de cita con más información
@login_required
def detalle_cita_completa(request, cita_id):
    """
    Vista para ver el detalle completo de una cita
    """
    try:
        cita = get_object_or_404(Cita, id=cita_id)
        
        # Verificar permisos
        user = request.user
        puede_ver = False
        
        if user.es_admin() or user.es_empleado() or user.es_veterinario():
            puede_ver = True
        elif user.es_cliente() and cita.propietario == user:
            puede_ver = True
        
        if not puede_ver:
            messages.error(request, "No tienes permiso para ver esta cita")
            return redirect('dashboard')
        
        # Obtener información adicional si existe
        mascota_info = None
        historial_relacionado = None
        
        if cita.mascota and hasattr(cita, 'mascota_id'):
            try:
                # Intentar obtener la mascota por ID si existe
                mascota_info = Mascota.objects.filter(id=cita.mascota_id).first()
            except:
                pass
        
        # Intentar obtener historial relacionado
        try:
            historial_relacionado = HistorialMedico.objects.filter(
                mascota__nombre=cita.mascota
            ).order_by('-fecha')[:3]
        except:
            pass
        
        context = {
            'cita': cita,
            'mascota_info': mascota_info,
            'historial_relacionado': historial_relacionado,
        }
        
        return render(request, "citas/detalle_cita_completa.html", context)
        
    except Exception as e:
        print(f"Error en detalle_cita_completa: {e}")
        messages.error(request, "Error al cargar los detalles de la cita")
        return redirect('citas:lista_citas')

@admin_required
def lista_usuarios(request):
    """
    Vista para listar todos los usuarios (solo admin)
    """
    usuarios = UsuariosRoles.objects.all().order_by('-date_joined')
    
    # Obtener conteos por rol
    total_usuarios = usuarios.count()
    clientes_count = usuarios.filter(groups__name='cliente').count()
    veterinarios_count = usuarios.filter(groups__name='veterinario').count()
    empleados_count = usuarios.filter(groups__name='empleado').count()
    admins_count = usuarios.filter(groups__name='admin').count()
    
    context = {
        'usuarios': usuarios,
        'total_usuarios': total_usuarios,
        'clientes_count': clientes_count,
        'veterinarios_count': veterinarios_count,
        'empleados_count': empleados_count,
        'admins_count': admins_count,
    }
    
    return render(request, "usuarios/lista_usuarios.html", context)

@admin_required
def cambiar_rol_usuario(request, user_id):
    """
    Vista para cambiar el rol de un usuario (solo admin)
    """
    if request.method == "POST":
        try:
            usuario = get_object_or_404(UsuariosRoles, id=user_id)
            nuevo_rol = request.POST.get('rol')
            
            if nuevo_rol in ['admin', 'empleado', 'cliente', 'veterinario']:
                # Limpiar grupos existentes
                usuario.groups.clear()
                
                # Agregar al nuevo grupo
                grupo, creado = Group.objects.get_or_create(name=nuevo_rol)
                usuario.groups.add(grupo)
                
                messages.success(request, f"Rol de {usuario.username} cambiado a {nuevo_rol}")
            else:
                messages.error(request, "Rol inválido")
                
        except Exception as e:
            print(f"Error al cambiar rol: {e}")
            messages.error(request, f"Error al cambiar rol: {str(e)}")
    
    return redirect('lista_usuarios')