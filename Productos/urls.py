from django.urls import path
from .views import ProductoFormView, ProductoListView

urlpatterns = [
    path("agregar/", ProductoFormView.as_view(), name="V_Productos"),
    path("listar/", ProductoListView.as_view(), name="agendar"),
]
