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
    cambiar_rol_usuario,
    registrar_mascota,
    agregar_producto,
    detalle_cita_completa,
    # Password reset
    RequestPasswordReset,
    PasswordResetConfirm,
    CustomPasswordResetView,
    CustomPasswordResetDoneView,
    CustomPasswordResetConfirmView,
    CustomPasswordResetCompleteView,
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
    path('mascotas/registrar/', registrar_mascota, name='registrar_mascota'),
    path('productos/agregar/', agregar_producto, name='agregar_producto'),
    path('citas/<int:cita_id>/detalle-completo/', detalle_cita_completa, name='detalle_cita_completa'),

    # ── API REST (para SPA / frontend separado) ──────────────────────────────
    path('reset-password/', RequestPasswordReset.as_view(), name='reset-password'),
    path('reset-password-confirm/<uidb64>/<token>/', PasswordResetConfirm.as_view(), name='reset-password-confirm'),

    # ── Flujo web tradicional (templates Django) ──────────────────────────────
    path('recuperar-password/', CustomPasswordResetView.as_view(), name='recuperar_password'),
    path('recuperar-password/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]