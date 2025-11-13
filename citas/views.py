# Create your views here.
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
from .models import Cita
from .forms import CitaForm
from django.http import Http404


class ListaCitasView(LoginRequiredMixin, ListView):
    model = Cita
    template_name = "citas/lista_citas.html"
    context_object_name = "citas"
    paginate_by = 10

    def get_queryset(self):
        return Cita.objects.filter(propietario=self.request.user).order_by(
            "fecha_cita", "hora_cita"
        )


class CrearCitaView(LoginRequiredMixin, CreateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas/crear_cita.html"
    success_url = reverse_lazy("citas:lista_citas")

    def form_valid(self, form):
        form.instance.propietario = self.request.user
        messages.success(self.request, "¡Cita agendada exitosamente!")
        return super().form_valid(form)


class EditarCitaView(LoginRequiredMixin, UpdateView):
    model = Cita
    form_class = CitaForm
    template_name = "citas/editar_cita.html"
    success_url = reverse_lazy("citas:lista_citas")

    def get_queryset(self):
        return Cita.objects.filter(propietario=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "¡Cita actualizada exitosamente!")
        return super().form_valid(form)


class EliminarCitaView(LoginRequiredMixin, DeleteView):
    model = Cita
    template_name = "citas/eliminar_cita.html"
    success_url = reverse_lazy("citas:lista_citas")

    def get_queryset(self):
        return Cita.objects.filter(propietario=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "¡Cita cancelada exitosamente!")
        return super().delete(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        cita = self.get_object()
        if cita.es_pasada:
            messages.error(request, "No puedes cancelar una cita que ya pasó.")
            return redirect("citas:lista_citas")
        return super().dispatch(request, *args, **kwargs)


class DetalleCitaView(LoginRequiredMixin, DetailView):
    model = Cita
    template_name = "citas/detalle_cita.html"
    context_object_name = "cita"

    def get_queryset(self):
        return Cita.objects.filter(propietario=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.propietario != self.request.user:
            raise Http404("No tienes permiso para ver esta cita")
        return obj


@login_required
def home_citas(request):
    return render(request, "citas/home_citas.html")
