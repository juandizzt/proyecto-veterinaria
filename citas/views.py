# citas/views.py
from django.shortcuts import render, redirect
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import Http404
from django.conf import settings  # Para usar el modelo de usuario personalizado
from django.utils import timezone

# Importar tu modelo de usuario personalizado
from usuarios.models import UsuariosRoles  # ← CAMBIAR
from .models import Cita
from .forms import CitaForm

# Importar decorators personalizados
from usuarios.decorators import (
    admin_required, 
    empleado_required, 
    cliente_required, 
    veterinario_required,
    rol_required
)

# ========== VISTAS GENERALES PARA TODOS LOS USUARIOS ==========

class ListaCitasView(LoginRequiredMixin, ListView):
    model = Cita
    template_name = "citas/lista_citas.html"
    context_object_name = "citas"
    paginate_by = 10

    def get_queryset(self):
        # Clientes solo ven sus propias citas
        if self.request.user.es_cliente():
            return Cita.objects.filter(propietario=self.request.user).order_by(
                "fecha_cita", "hora_cita"
            )
        # Empleados y veterinarios ven todas las citas
        elif self.request.user.es_empleado() or self.request.user.es_veterinario():
            return Cita.objects.all().order_by("fecha_cita", "hora_cita")
        # Administradores ven todas las citas
        elif self.request.user.es_admin():
            return Cita.objects.all().order_by("fecha_cita", "hora_cita")
        return Cita.objects.none()

class CrearCitaView(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas/crear_cita.html"
    success_url = reverse_lazy("citas:lista_citas")

    def form_valid(self, form):
        form.instance.propietario = self.request.user
        messages.success(self.request, "¡Cita agendada exitosamente!")
        return super().form_valid(form)

    # Solo clientes pueden crear citas
    def dispatch(self, request, *args, **kwargs):
        if not request.user.es_cliente():
            messages.error(request, "Solo los clientes pueden agendar citas.")
            return redirect('citas:lista_citas')
        return super().dispatch(request, *args, **kwargs)

class EditarCitaView(LoginRequiredMixin, UpdateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas/editar_cita.html"
    success_url = reverse_lazy("citas:lista_citas")

    def get_queryset(self):
        # Clientes solo pueden editar sus propias citas
        if self.request.user.es_cliente():
            return Cita.objects.filter(propietario=self.request.user)
        # Empleados, veterinarios y admins pueden editar todas
        else:
            return Cita.objects.all()

    def form_valid(self, form):
        messages.success(self.request, "¡Cita actualizada exitosamente!")
        return super().form_valid(form)

class EliminarCitaView(LoginRequiredMixin, DeleteView):
    model = Cita
    template_name = "citas/eliminar_cita.html"
    success_url = reverse_lazy("citas:lista_citas")

    def get_queryset(self):
        # Clientes solo pueden eliminar sus propias citas
        if self.request.user.es_cliente():
            return Cita.objects.filter(propietario=self.request.user)
        # Empleados, veterinarios y admins pueden eliminar todas
        else:
            return Cita.objects.all()

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "¡Cita cancelada exitosamente!")
        return super().delete(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        cita = self.get_object()
        if cita.es_pasada and request.user.es_cliente():
            messages.error(request, "No puedes cancelar una cita que ya pasó.")
            return redirect("citas:lista_citas")
        return super().dispatch(request, *args, **kwargs)

class DetalleCitaView(LoginRequiredMixin, DetailView):
    model = Cita
    template_name = "citas/detalle_cita.html"
    context_object_name = "cita"

    def get_queryset(self):
        # Clientes solo pueden ver sus propias citas
        if self.request.user.es_cliente():
            return Cita.objects.filter(propietario=self.request.user)
        # Otros roles pueden ver todas
        else:
            return Cita.objects.all()

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        # Clientes solo pueden ver sus propias citas
        if self.request.user.es_cliente() and obj.propietario != self.request.user:
            raise Http404("No tienes permiso para ver esta cita")
        return obj

@login_required
def home_citas(request):
    return render(request, "citas/home_citas.html")

# ========== VISTAS SOLO PARA ADMINISTRADORES ==========

@admin_required
def historial_citas(request):
    """Historial completo de todas las citas (solo admin)"""
    citas = Cita.objects.all().order_by("-fecha_cita", "-hora_cita")
    return render(request, "citas/historial_citas.html", {"citas": citas})

@rol_required('admin', 'veterinario')
def historial_mascota(request, nombre_mascota):
    """Historial de citas de una mascota específica"""
    citas = Cita.objects.filter(mascota=nombre_mascota).order_by("-fecha_cita", "-hora_cita")
    
    return render(request, "citas/historial_mascota.html", {
        "mascota": nombre_mascota,
        "citas": citas,
    })

@admin_required
def historial_usuario(request, username):
    """Historial de citas de un usuario específico (solo admin)"""
    try:
        usuario = UsuariosRoles.objects.get(username=username)  # ← CAMBIAR de User a UsuariosRoles
    except UsuariosRoles.DoesNotExist:
        messages.error(request, f"Usuario {username} no encontrado")
        return redirect('citas:listado_mascotas')

    citas = Cita.objects.filter(propietario=usuario).order_by("-fecha_cita", "-hora_cita")
    
    # Obtener todas las mascotas desde las citas
    mascotas = (
        Cita.objects.filter(propietario=usuario)
        .values_list("mascota", flat=True)
        .distinct()
    )

    return render(request, "citas/historial_usuario.html", {
        "usuario": usuario,
        "citas": citas,
        "mascotas": mascotas
    })

@rol_required('admin', 'empleado', 'veterinario')
def listado_mascotas(request):
    """Listado de todas las mascotas (admin, empleado, veterinario)"""
    mascotas = (
        Cita.objects.values_list("mascota", flat=True)
        .distinct()
        .order_by("mascota")
    )

    return render(request, "citas/listado_mascotas.html", {
        "mascotas": mascotas
    })

# ========== VISTAS PARA EMPLEADOS Y VETERINARIOS ==========

@rol_required('empleado', 'veterinario')
def citas_hoy(request):
    """Citas programadas para hoy"""
    hoy = timezone.now().date()
    citas = Cita.objects.filter(fecha_cita=hoy).order_by('hora_cita')
    
    return render(request, "citas/citas_hoy.html", {
        "citas": citas,
        "fecha": hoy
    })

@rol_required('empleado', 'veterinario')
def citas_pendientes(request):
    """Citas pendientes de confirmación"""
    citas = Cita.objects.filter(estado='pendiente').order_by('fecha_cita', 'hora_cita')
    
    return render(request, "citas/citas_pendientes.html", {
        "citas": citas
    })

@rol_required('empleado', 'veterinario', 'admin')
def cambiar_estado_cita(request, pk):
    """Cambiar estado de una cita"""
    if request.method == "POST":
        try:
            cita = Cita.objects.get(pk=pk)
            nuevo_estado = request.POST.get('estado')
            
            if nuevo_estado in dict(Cita.ESTADO_CHOICES).keys():
                cita.estado = nuevo_estado
                cita.save()
                messages.success(request, f"Estado de la cita cambiado a {cita.get_estado_display()}")
            else:
                messages.error(request, "Estado inválido")
                
        except Cita.DoesNotExist:
            messages.error(request, "Cita no encontrada")
    
    return redirect('citas:lista_citas')