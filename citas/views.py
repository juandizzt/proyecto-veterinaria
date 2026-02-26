# citas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.http import Http404
from django.utils import timezone

# Modelos y Forms de la App CITAS
from .models import Cita
from .forms import CitaForm

# MODELOS Y FORMS DE LA APP MASCOTAS (Importación corregida)
from mascotas.models import Mascota
from mascotas.forms import MascotaForm

# Importar tu modelo de usuario personalizado
from usuarios.models import UsuariosRoles 

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
        if self.request.user.es_cliente():
            return Cita.objects.filter(propietario=self.request.user).order_by("fecha_cita", "hora_cita")
        elif self.request.user.es_empleado() or self.request.user.es_veterinario() or self.request.user.es_admin():
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
        if self.request.user.es_cliente():
            return Cita.objects.filter(propietario=self.request.user)
        return Cita.objects.all()

    def form_valid(self, form):
        messages.success(self.request, "¡Cita actualizada exitosamente!")
        return super().form_valid(form)

class EliminarCitaView(LoginRequiredMixin, DeleteView):
    model = Cita
    template_name = "citas/eliminar_cita.html"
    success_url = reverse_lazy("citas:lista_citas")

    def get_queryset(self):
        if self.request.user.es_cliente():
            return Cita.objects.filter(propietario=self.request.user)
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
        if self.request.user.es_cliente():
            return Cita.objects.filter(propietario=self.request.user)
        return Cita.objects.all()

@login_required
def home_citas(request):
    return render(request, "citas/home_citas.html")

# ========== VISTAS SOLO PARA ADMINISTRADORES/VETERINARIOS ==========

@admin_required
def historial_citas(request):
    citas = Cita.objects.all().order_by("-fecha_cita", "-hora_cita")
    return render(request, "citas/historial.html", {"citas": citas})

@rol_required('admin', 'veterinario')
def historial_mascota(request, mascota_id):
    mascota = get_object_or_404(Mascota, id=mascota_id)
    citas = Cita.objects.filter(mascota=mascota.nombre).order_by('-fecha_cita', '-hora_cita')
    return render(request, 'citas/historial_mascota.html', {'mascota': mascota, 'citas': citas})

@admin_required
def historial_usuario(request, username):
    try:
        usuario = UsuariosRoles.objects.get(username=username)
    except UsuariosRoles.DoesNotExist:
        messages.error(request, f"Usuario {username} no encontrado")
        return redirect('citas:listado_mascotas')

    citas = Cita.objects.filter(propietario=usuario).order_by("-fecha_cita", "-hora_cita")
    mascotas = Cita.objects.filter(propietario=usuario).values_list("mascota", flat=True).distinct()

    return render(request, "citas/historial_usuario.html", {
        "usuario": usuario, "citas": citas, "mascotas": mascotas
    })

@rol_required('admin', 'empleado', 'veterinario')
def listado_mascotas(request):
    mascotas = Mascota.objects.all().order_by('nombre')
    return render(request, "citas/listado_mascotas.html", {"mascotas": mascotas})

# ========== GESTIÓN DE MASCOTAS (EDICIÓN) ==========

@rol_required('admin', 'empleado', 'veterinario')
def editar_mascota(request, mascota_id):
    # Obtiene la mascota o lanza un error 404 si no existe
    mascota = get_object_or_404(Mascota, id=mascota_id) 
    
    if request.method == 'POST':
        # instance=mascota es CLAVE para que Django sepa que debe ACTUALIZAR y no CREAR uno nuevo
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            form.save()
            messages.success(request, f"La información de {mascota.nombre} ha sido actualizada.")
            return redirect('citas:listado_mascotas')
    else:
        # instance=mascota carga los datos actuales (nombre, especie, etc.) en los cuadros de texto
        form = MascotaForm(instance=mascota)
    
    return render(request, 'mascotas/registrar_mascota.html', {
        'form': form,
        'mascota': mascota,  # Enviamos el objeto mascota para que el HTML sepa que estamos editando
    })
# ========== VISTAS PARA EMPLEADOS Y VETERINARIOS ==========

@rol_required('empleado', 'veterinario')
def citas_hoy(request):
    hoy = timezone.now().date()
    citas = Cita.objects.filter(fecha_cita=hoy).order_by('hora_cita')
    return render(request, "citas/citas_hoy.html", {"citas": citas, "fecha": hoy})

@rol_required('empleado', 'veterinario')
def citas_pendientes(request):
    citas = Cita.objects.filter(estado='pendiente').order_by('fecha_cita', 'hora_cita')
    return render(request, "citas/citas_pendientes.html", {"citas": citas})

@rol_required('empleado', 'veterinario', 'admin')
def cambiar_estado_cita(request, pk):
    if request.method == "POST":
        try:
            cita = Cita.objects.get(pk=pk)
            nuevo_estado = request.POST.get('estado')
            if nuevo_estado in dict(Cita.ESTADO_CHOICES).keys():
                cita.estado = nuevo_estado
                cita.save()
                messages.success(request, f"Estado de la cita cambiado a {cita.get_estado_display()}")
        except Cita.DoesNotExist:
            messages.error(request, "Cita no encontrada")
    return redirect('citas:lista_citas')

def gestionar_mascota(request, mascota_id=None):
    if mascota_id:
        # Modo Edición: Carga la mascota existente
        mascota = get_object_or_404(Mascota, id=mascota_id)
        form = MascotaForm(request.POST or None, request.FILES or None, instance=mascota)
    else:
        # Modo Registro: Formulario vacío
        mascota = None
        form = MascotaForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('citas:listado_mascotas')

    # Usamos el mismo template para ambos para mantener el diseño centrado
    return render(request, 'mascotas/registrar_mascota.html', {
        'form': form,
        'mascota': mascota
    })