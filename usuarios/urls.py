# usuarios/urls.py
from django.urls import path
from .views import (
    registro_view, 
    login_view, 
    logout_view, 
    dashboard_view,
    dashboard_admin,
    dashboard_empleado,
    dashboard_cliente,
    dashboard_veterinario,
    lista_usuarios,
    cambiar_rol_usuario
)

urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('registro/', registro_view, name='registrar'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/admin/', dashboard_admin, name='dashboard_admin'),
    path('dashboard/empleado/', dashboard_empleado, name='dashboard_empleado'),
    path('dashboard/cliente/', dashboard_cliente, name='dashboard_cliente'),
    path('dashboard/veterinario/', dashboard_veterinario, name='dashboard_veterinario'),
    path('usuarios/', lista_usuarios, name='lista_usuarios'),
    path('usuarios/<int:user_id>/cambiar-rol/', cambiar_rol_usuario, name='cambiar_rol_usuario'),
]