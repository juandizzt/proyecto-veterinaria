from django.urls import path
from .views import CrearPedidoProductosView,MypedidoView

urlpatterns = [
    path("mi-pedido", MypedidoView.as_view(), name="mi_pedido"),
    path('agregar_producto/', CrearPedidoProductosView.as_view(), name='agregar_producto'),
]
