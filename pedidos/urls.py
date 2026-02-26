# pedidos/urls.py - VERSIÓN DEFINITIVA
from django.urls import path
from . import views

urlpatterns = [
    path('mi-pedido/', views.mi_pedido_funcion, name='mi_pedido'),
    path('agregar-producto-ajax/', views.agregar_producto_ajax, name='agregar_producto_ajax'),
    path('eliminar-detalle/<int:detalle_id>/', views.eliminar_detalle, name='eliminar_detalle'),
    path('actualizar-cantidad/<int:detalle_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('hacer-pedido/', views.hacer_pedido, name='hacer_pedido'),

    # ✅ AGREGAR ESTAS DOS:
    path('confirmar/', views.confirmar_pedido, name='confirmar_pedido'),
    path('detalle-admin/<int:pedido_id>/', views.detalle_pedido_admin, name='detalle_pedido_admin'),
]