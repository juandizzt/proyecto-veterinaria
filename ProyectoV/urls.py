"""
URL configuration for ProyectoV project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# urls.py global - CORREGIDO
# ProyectoV/urls.py (CORREGIDO - versión sin namespaces)

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views 
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path("admin/", admin.site.urls),
    path("productos/", include("Productos.urls")),  # SIN namespace
    path("usuarios/", include("usuarios.urls")),    # SIN namespace
    path("pedidos/", include("pedidos.urls")),      # SIN namespace
    path("citas/", include("citas.urls")), 
    path('mascotas/', include('mascotas.urls',)),        # SIN namespace
    path('inicio/', views.inicio, name='inicio'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path("historialM/", include("historialM.urls")), # SIN namespace
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)