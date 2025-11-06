from django.urls import path
from .views import ProductoFormView

urlpatterns = [
    path("agregar/", ProductoFormView.as_view(), name="V_Productos"),
]
