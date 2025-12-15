# Productos/views.py - VERSIÓN COMPLETA CORREGIDA
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required  # ¡ESTO FALTABA!
from django.http import JsonResponse
from .models import Producto
from django.db.models import Sum
import json
from django.contrib.auth.decorators import user_passes_test

# 1. FUNCIÓN PARA LISTAR PRODUCTOS (DEBE EXISTIR)
def ProductoListView(request):
    productos = Producto.objects.all()
    
    # Obtener el conteo del carrito de manera segura
    carrito_count = 0
    if request.user.is_authenticated:
        try:
            from pedidos.models import Pedido, DetallePedido
            
            carrito_count = DetallePedido.objects.filter(
                pedido__usuario=request.user,
                pedido__estado='PENDIENTE'
            ).aggregate(total_items=Sum('cantidad'))['total_items'] or 0
        except Exception as e:
            print(f"Error en ProductoListView: {e}")
            carrito_count = 0
    
    return render(request, 'Productos/lista.html', {
        'productos': productos,
        'carrito_count': carrito_count
    })

# 2. FUNCIÓN PARA AGREGAR PRODUCTOS AL PEDIDO (AJAX) - CORREGIDA
@login_required
def agregar_producto_ajax(request):
    if request.method == 'POST':
        try:
            # Importar los modelos de pedidos
            from pedidos.models import Pedido, DetallePedido
            from django.db.models import Sum
            
            producto_id = request.POST.get('producto_id')
            cantidad = int(request.POST.get('cantidad', 1))
            
            # Obtener el producto por su código (NO por id)
            try:
                producto = Producto.objects.get(codigo=producto_id)
            except Producto.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Producto no encontrado'
                })
            
            # Verificar stock
            if producto.stock < cantidad:
                return JsonResponse({
                    'success': False,
                    'error': f'Stock insuficiente. Solo hay {producto.stock} unidades disponibles.',
                    'nuevo_stock': producto.stock
                })
            
            # Obtener o crear el pedido activo del usuario
            pedido, creado = Pedido.objects.get_or_create(
                usuario=request.user,
                estado='PENDIENTE',
                defaults={'total': 0}
            )
            
            # Verificar si el producto ya está en el pedido
            detalle_existente = DetallePedido.objects.filter(
                pedido=pedido,
                producto=producto
            ).first()
            
            if detalle_existente:
                # Actualizar cantidad existente
                nueva_cantidad = detalle_existente.cantidad + cantidad
                if producto.stock < nueva_cantidad:
                    return JsonResponse({
                        'success': False,
                        'error': f'No hay suficiente stock. Stock disponible: {producto.stock}',
                        'nuevo_stock': producto.stock
                    })
                
                detalle_existente.cantidad = nueva_cantidad
                detalle_existente.save()
                detalle = detalle_existente
            else:
                # Crear nuevo detalle
                detalle = DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad
                )
            
            # Actualizar stock del producto
            producto.stock -= cantidad
            producto.save()
            
            # Actualizar total del pedido
            total_pedido = DetallePedido.objects.filter(pedido=pedido).aggregate(
                total=Sum('subtotal')
            )['total'] or 0
            pedido.total = total_pedido
            pedido.save()
            
            # Calcular el conteo total de items en el carrito
            carrito_count = DetallePedido.objects.filter(pedido=pedido).aggregate(
                total_items=Sum('cantidad')
            )['total_items'] or 0
            
            return JsonResponse({
                'success': True,
                'carrito_count': carrito_count,
                'nuevo_stock': producto.stock,
                'mensaje': f'Producto agregado exitosamente'
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False, 
                'error': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Solicitud inválida'})

# 3. FUNCIÓN PARA OBTENER CONTEO DEL CARRITO
def obtener_carrito_count(request):
    if request.user.is_authenticated:
        try:
            from pedidos.models import Pedido, DetallePedido
            
            carrito_count = DetallePedido.objects.filter(
                pedido__usuario=request.user,
                pedido__estado='PENDIENTE'
            ).aggregate(total_items=Sum('cantidad'))['total_items'] or 0
            
            return JsonResponse({'carrito_count': carrito_count})
        except Exception as e:
            print(f"Error al obtener carrito count: {e}")
            return JsonResponse({'carrito_count': 0})
    
    return JsonResponse({'carrito_count': 0})

# 4. OPCIONAL: CLASE PARA FORMULARIO DE PRODUCTO (si la necesitas)
# Si NO la necesitas, COMENTA o ELIMINA esta sección
'''
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

class ProductoFormView(LoginRequiredMixin, CreateView):
    model = Producto
    fields = ['nombre', 'descripcion', 'precio', 'stock', 'imagen']
    template_name = 'Productos/v_producto.html'
    success_url = reverse_lazy('lista')
    
    def form_valid(self, form):
        return super().form_valid(form)
'''

def es_admin_o_empleado(user):
    return user.groups.filter(name__in=["admin","empleado"]).exists()

@user_passes_test(es_admin_o_empleado)
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, "productos/lista.html", {"productos": productos})

@user_passes_test(es_admin_o_empleado)
def editar_producto(request, id):
    producto = Producto.objects.get(id=id)
    if request.method == "POST":
        producto.nombre = request.POST["nombre"]
        producto.descripcion = request.POST["descripcion"]
        producto.precio = request.POST["precio"]
        producto.cantidad = request.POST["cantidad"]
        producto.save()
        return redirect("lista_productos")

    return render(request, "productos/editar.html", {"producto": producto})
