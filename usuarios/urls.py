from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from .views import RegistrarView


urlpatterns = [
    path(
        "login/", LoginView.as_view(template_name="usuarios/login.html"), name="login"
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("registro/", RegistrarView.as_view(), name="registrar"),
]
