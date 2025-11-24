from django.urls import path
from . import views

app_name = 'historialM'

urlpatterns = [
    path('', views.dashboard_veterinario, name='dashboard'),
    path('lista/', views.ListaHistorialesView.as_view(), name='lista_historiales'),
    path('crear/', views.CrearHistorialView.as_view(), name='crear_historial'),
    path('detalle/<int:pk>/', views.DetalleHistorialView.as_view(), name='detalle_historial'),
    
]