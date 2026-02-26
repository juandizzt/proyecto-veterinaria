# mascotas/urls.py
# mascotas/urls.py - Debe verse así exactamente
from django.urls import path
from . import views

app_name = 'mascotas'  # ← CAMBIAR

urlpatterns = [
    path('registrar/', views.registrar_mascota, name='registrar_mascota'),
    path('editar/<int:pk>/', views.registrar_mascota, name='editar_mascota'),
    path('lista/', views.ListaMascotasView.as_view(), name='lista_mascotas_registradas'),
]