from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.urls import reverse_lazy
from .models import HistorialMedico

def es_veterinario(user):
    return user.groups.filter(name='Veterinarios').exists() or user.is_superuser

class SoloVeterinariosMixin(UserPassesTestMixin):
    def test_func(self):
        return es_veterinario(self.request.user)

class ListaHistorialesView(SoloVeterinariosMixin, ListView):
    model = HistorialMedico
    template_name = "historialM/lista_historiales.html"
    context_object_name = "historiales"
    paginate_by = 20

    def get_queryset(self):
        # Los veterinarios solo ven los historiales que ellos crearon
        # Los superusuarios ven todos
        if self.request.user.is_superuser:
            return HistorialMedico.objects.all()
        return HistorialMedico.objects.filter(veterinario=self.request.user)

class DetalleHistorialView(SoloVeterinariosMixin, DetailView):
    model = HistorialMedico
    template_name = "historialM/detalle_historial.html"
    context_object_name = "historial"

class CrearHistorialView(SoloVeterinariosMixin, CreateView):
    model = HistorialMedico
    template_name = "historialM/crear_historial.html"
    fields = [
        'cita', 'tipo_consulta', 'diagnostico', 'tratamiento', 
        'medicamentos', 'observaciones', 'peso', 'temperatura',
        'estado_salud', 'proxima_cita', 'es_urgente'
    ]
    success_url = reverse_lazy('historialM:lista_historiales')

    def form_valid(self, form):
        form.instance.veterinario = self.request.user
        # Copiar información de la cita seleccionada
        if form.instance.cita:
            form.instance.mascota = form.instance.cita.mascota
            form.instance.propietario = form.instance.cita.propietario
            form.instance.tipo_mascota = form.instance.cita.tipo_mascota
            form.instance.fecha_consulta = form.instance.cita.fecha_cita
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Filtrar citas para mostrar solo las completadas/pasadas
        from django.utils import timezone
        from citas.models import Cita
        form.fields['cita'].queryset = Cita.objects.filter(
            fecha_cita__lte=timezone.now().date()
        )
        return form

@user_passes_test(es_veterinario)
def dashboard_veterinario(request):
    from django.utils import timezone
    from datetime import timedelta
    
    # Estadísticas para el dashboard del veterinario
    hoy = timezone.now().date()
    ultima_semana = hoy - timedelta(days=7)
    
    total_historiales = HistorialMedico.objects.filter(veterinario=request.user).count()
    historiales_urgentes = HistorialMedico.objects.filter(
        veterinario=request.user, 
        es_urgente=True
    ).count()
    historiales_recientes = HistorialMedico.objects.filter(
        veterinario=request.user,
        fecha_consulta__gte=ultima_semana
    ).count()
    
    context = {
        'total_historiales': total_historiales,
        'historiales_urgentes': historiales_urgentes,
        'historiales_recientes': historiales_recientes,
    }
    
    return render(request, 'historialM/dashboard_veterinario.html', context)