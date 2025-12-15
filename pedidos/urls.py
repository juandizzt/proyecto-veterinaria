# pedidos/urls.py - VERSIÓN DEFINITIVA
from django.urls import path
from . import views

urlpatterns = [
    # Vista principal del pedido
    path('mi-pedido/', views.mi_pedido_funcion, name='mi_pedido'),
    
    # AJAX para agregar productos
    path('agregar-producto-ajax/', views.agregar_producto_ajax, name='agregar_producto_ajax'),
    
    # Acciones sobre el pedido
    path('eliminar/<int:detalle_id>/', views.eliminar_detalle, name='eliminar_detalle'),
    path('actualizar/<int:detalle_id>/', views.actualizar_cantidad, name='actualizar_cantidad'),
]