from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from .models import Cita

def es_admin(user):
    return user.groups.filter(name='admin').exists()

@user_passes_test(es_admin)
def historial_mascota(request, nombre):
    citas = Cita.objects.filter(mascota=nombre).order_by("-fecha_cita", "-hora_cita")
    return render(request, "citas/historial_mascota.html", {
        "citas": citas,
        "nombre": nombre
    })