from django.urls import path
from .views import CrearPedidoProductosView,MypedidoView, EditarPedidoProductoView, EliminarPedidoProductoView

urlpatterns = [
    path("mi-pedido", MypedidoView.as_view(), name="mi_pedido"),
    path('agregar_producto/', CrearPedidoProductosView.as_view(), name='agregar_producto'),
    path('editar_producto/<int:pk>/', EditarPedidoProductoView.as_view(), name='editar_producto'),
    path('eliminar_producto/<int:pk>/', EliminarPedidoProductoView.as_view(), name='eliminar_producto'),
]
