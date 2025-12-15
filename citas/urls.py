# citas/urls.py
from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    # VISTAS GENERALES (todos los usuarios autenticados)
    path('', views.home_citas, name='home_citas'),
    path('lista/', views.ListaCitasView.as_view(), name='lista_citas'),
    path('crear/', views.CrearCitaView.as_view(), name='crear_cita'),
    path('editar/<int:pk>/', views.EditarCitaView.as_view(), name='editar_cita'),
    path('eliminar/<int:pk>/', views.EliminarCitaView.as_view(), name='eliminar_cita'),
    path('detalle/<int:pk>/', views.DetalleCitaView.as_view(), name='detalle_cita'),
    
    # VISTAS DE ADMINISTRACIÓN (solo admin)
    path('historial/', views.historial_citas, name='historial_citas'),
    path('historial/usuario/<str:username>/', views.historial_usuario, name='historial_usuario'),
    
    # VISTAS PARA EMPLEADOS/VETERINARIOS/ADMIN
    path('listado_mascotas/', views.listado_mascotas, name='listado_mascotas'),
    path('historial/mascota/<str:nombre_mascota>/', views.historial_mascota, name='historial_mascota'),
    
    # VISTAS PARA GESTIÓN OPERATIVA (empleados y veterinarios)
    path('citas/hoy/', views.citas_hoy, name='citas_hoy'),
    path('citas/pendientes/', views.citas_pendientes, name='citas_pendientes'),
    path('cambiar-estado/<int:pk>/', views.cambiar_estado_cita, name='cambiar_estado_cita'),
]