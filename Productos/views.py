from django.views.generic.edit import FormView
from .forms import ProductForm  # clase ProductoForm importada


class ProductoFormView(FormView):
    template_name = "Productos/V_Productos.html"
    form_class = ProductForm
