from django.urls import path
from . import views

app_name = 'citas'

urlpatterns = [
    path('', views.home_citas, name='home_citas'),
    path('lista/', views.ListaCitasView.as_view(), name='lista_citas'),
    path('crear/', views.CrearCitaView.as_view(), name='crear_cita'),
    path('editar/<int:pk>/', views.EditarCitaView.as_view(), name='editar_cita'),
    path('eliminar/<int:pk>/', views.EliminarCitaView.as_view(), name='eliminar_cita'),
    path('detalle/<int:pk>/', views.DetalleCitaView.as_view(), name='detalle_cita'),
]