from django.urls import path
from .views import MypedidoView

urlpatterns = [
    path("mi-pedido", MypedidoView.as_view(), name="mi_pedido"),
]
