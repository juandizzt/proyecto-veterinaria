# mascotas/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.contrib.auth import get_user_model
from .models import Mascota
from .forms import MascotaForm
from usuarios.decorators import cliente_required, rol_required

# ========== VISTAS PARA CLIENTES ==========
User = get_user_model()

@login_required
@cliente_required
def registrar_mascota(request, pk=None):
    """
    Vista para crear y editar mascotas.
    Si se recibe un pk, se edita; si no, se crea una nueva.
    """
    mascota = None
    
    # Si hay un pk, estamos editando
    if pk:
        mascota = get_object_or_404(Mascota, pk=pk)
        titulo = "Editar Mascota"
    else:
        titulo = "Registrar Nueva Mascota"
    
    if request.method == 'POST':
        form = MascotaForm(request.POST, instance=mascota)
        if form.is_valid():
            form.save()
            return redirect('mascotas:lista_mascotas')
    else:
        form = MascotaForm(instance=mascota)
    
    return render(request, 'mascotas/registrar_mascota.html', {
        'form': form,
        'titulo': titulo,
        'mascota': mascota
    })
@login_required
@cliente_required
def editar_mascota(request, mascota_id):
    """Vista para que los clientes editen sus mascotas"""
    mascota = get_object_or_404(Mascota, id=mascota_id, dueño=request.user)
    
    if request.method == 'POST':
        form = MascotaForm(request.POST, instance=mascota)
        if form.is_valid():
            form.save()
            messages.success(request, f'¡{mascota.nombre} ha sido actualizado(a) exitosamente!')
            return redirect('mascotas:lista_mascotas')
    else:
        form = MascotaForm(instance=mascota)
    
    return render(request, 'mascotas/registrar_mascota.html', {
        'form': form,
        'titulo': f'Editar Mascota: {mascota.nombre}',
        'mascota': mascota
    })

@login_required
@cliente_required
def eliminar_mascota(request, mascota_id):
    """Vista para que los clientes eliminen sus mascotas"""
    mascota = get_object_or_404(Mascota, id=mascota_id, dueño=request.user)
    
    if request.method == 'POST':
        nombre = mascota.nombre
        mascota.delete()
        messages.success(request, f'¡{nombre} ha sido eliminado(a) del registro!')
        return redirect('mascotas:lista_mascotas')
    
    return render(request, 'mascotas/eliminar_mascota.html', {
        'mascota': mascota
    })
# mascotas/views.py - Agrega esta función

# ========== VISTAS PARA TODOS LOS ROLES ==========

class ListaMascotasView(LoginRequiredMixin, ListView):
    """Vista para listar mascotas (todos los roles pueden ver)"""
    model = Mascota
    template_name = 'mascotas/lista_mascotas_registradas.html'
    context_object_name = 'mascotas'
    paginate_by = 10
    
    def get_queryset(self):
        # Clientes solo ven sus propias mascotas
        if self.request.user.es_cliente():
            return Mascota.objects.filter(dueño=self.request.user).order_by('-fecha_registro')
        # Empleados, veterinarios y administradores ven todas las mascotas
        else:
            return Mascota.objects.all().order_by('-fecha_registro')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['es_cliente'] = self.request.user.es_cliente()
        return context

@login_required
def detalle_mascota(request, mascota_id):
    """Vista para ver el detalle de una mascota"""
    # Clientes solo pueden ver sus propias mascotas
    if request.user.es_cliente():
        mascota = get_object_or_404(Mascota, id=mascota_id, dueño=request.user)
    else:
        # Otros roles pueden ver cualquier mascota
        mascota = get_object_or_404(Mascota, id=mascota_id)
    
    # Obtener citas relacionadas con esta mascota
    from citas.models import Cita
    citas = Cita.objects.filter(mascota=mascota.nombre).order_by('-fecha_cita')[:5]
    
    return render(request, 'mascotas/detalle_mascota.html', {
        'mascota': mascota,
        'citas': citas
    })