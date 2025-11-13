from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView
from .models import Pedido


class MypedidoView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = "pedidos/Ordenes.html"
    context_object_name = "pedido"

    def get_object(self, queryset=None):
        return Pedido.objects.filter(usuario=self.request.user, is_active=True).first()


# Create your views here.
