from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, CreateView
from .models import Pedido
from django.urls import reverse_lazy
from .forms import PedidoProductoForm


class MypedidoView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = "pedidos/Ordenes.html"
    context_object_name = "pedido"

    def get_object(self, queryset=None):
        return Pedido.objects.filter(usuario=self.request.user, is_active=True).first()


# Create your views here.

class CrearPedidoProductosView(LoginRequiredMixin, CreateView):
    template_name = "pedidos/crear_pedidos.html"
    form_class = PedidoProductoForm
    success_url = reverse_lazy("mi_pedido")

    def form_valid(self, form):
        pedido, _ = Pedido.objects.get_or_create(
            is_active=True,
            usuario=self.request.user,
        )
        form.instance.pedido = pedido
        form.instance.cantidad = 1
        form.save()
        return super().form_valid(form)