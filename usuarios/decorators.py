# usuarios/decorators.py
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    Decorator que verifica si el usuario es administrador.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.es_admin(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def empleado_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    Decorator que verifica si el usuario es empleado.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.es_empleado(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def cliente_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    Decorator que verifica si el usuario es cliente.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.es_cliente(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def veterinario_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url='login'):
    """
    Decorator que verifica si el usuario es veterinario.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.es_veterinario(),
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def rol_required(*roles):
    """
    Decorator que verifica si el usuario tiene alguno de los roles especificados.
    Uso: @rol_required('admin', 'empleado')
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Debes iniciar sesión para acceder a esta página.")
                return redirect('login')
            
            if not hasattr(request.user, 'rol'):
                messages.error(request, "Tu cuenta no tiene un rol asignado.")
                return redirect('login')
            
            if request.user.rol not in roles:
                messages.error(request, "No tienes permisos para acceder a esta página.")
                return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator