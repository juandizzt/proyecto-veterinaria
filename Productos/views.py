from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from .forms import ProductForm
from django.urls import reverse_lazy
from .models import Producto


class ProductoFormView(FormView):
    template_name = "productos/V_Producto.html"
    form_class = ProductForm
    success_url = reverse_lazy("V_Productos")  # Agregar URL de éxito

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ProductoListView(ListView):
    model = Producto
    template_name = "productos/lista.html"
    context_object_name = "productos"

    def get_queryset(self):
        return Producto.objects.all().order_by("nombre")
