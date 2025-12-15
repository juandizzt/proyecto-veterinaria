# Productos/urls.py - VERSIÓN CORREGIDA
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductoListView, name='lista'),
    path('agregar-producto-ajax/', views.agregar_producto_ajax, name='agregar_producto_ajax'),
    path('obtener-carrito-count/', views.obtener_carrito_count, name='obtener_carrito_count'),
    
    # Solo incluye esta línea si necesitas ProductoFormView (y está descomentada en views.py)
    # path('agregar/', views.ProductoFormView.as_view(), name='agregar_producto'),
]