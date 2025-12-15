# pedidos/views.py - VERSIÓN DEFINITIVA
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum

from .models import Pedido, DetallePedido
from Productos.models import Producto

# ========== VISTA PRINCIPAL DEL PEDIDO ==========

@login_required
def mi_pedido_funcion(request):
    """
    Vista principal para ver el pedido del usuario
    """
    try:
        # Obtener o crear pedido PENDIENTE
        pedido, created = Pedido.objects.get_or_create(
            usuario=request.user,
            estado='PENDIENTE',
            defaults={'total': 0}
        )
        
        # Obtener los detalles del pedido
        detalles = DetallePedido.objects.filter(pedido=pedido)
        
        return render(request, "pedidos/Ordenes.html", {
            'pedido': pedido,
            'detalles': detalles,
        })
        
    except Exception as e:
        messages.error(request, f"Error al cargar el pedido: {str(e)}")
        return render(request, "pedidos/Ordenes.html", {
            'pedido': None,
            'detalles': [],
        })

# ========== VISTA PARA AGREGAR PRODUCTO (AJAX) ==========

@login_required
def agregar_producto_ajax(request):
    """
    Vista para agregar productos al pedido via AJAX
    """
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            producto_id = request.POST.get('producto_id')
            cantidad_str = request.POST.get('cantidad', '1')
            
            # Validar y convertir datos
            if not producto_id or not cantidad_str:
                return JsonResponse({
                    'success': False,
                    'error': 'Datos incompletos'
                })
            
            try:
                cantidad = int(cantidad_str)
                if cantidad <= 0:
                    raise ValueError
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Cantidad inválida'
                })
            
            # Buscar el producto por código (NO por id)
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
            
            # Obtener o crear pedido activo
            pedido, _ = Pedido.objects.get_or_create(
                usuario=request.user,
                estado='PENDIENTE',
                defaults={'total': 0}
            )
            
            # Buscar si el producto ya está en el pedido
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
                detalle_existente.save()  # El save() recalcula subtotal automáticamente
                detalle = detalle_existente
                
            else:
                # Crear nuevo detalle
                detalle = DetallePedido.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad=cantidad
                )
                # El subtotal se calcula automáticamente en save()
            
            # Actualizar stock del producto
            producto.stock -= cantidad
            producto.save()
            
            # Recalcular total del pedido
            total_pedido = DetallePedido.objects.filter(
                pedido=pedido
            ).aggregate(total=Sum('subtotal'))['total'] or 0
            pedido.total = total_pedido
            pedido.save()
            
            # Calcular cantidad total de items en el carrito
            carrito_count = DetallePedido.objects.filter(
                pedido=pedido
            ).aggregate(total_items=Sum('cantidad'))['total_items'] or 0
            
            return JsonResponse({
                'success': True,
                'carrito_count': carrito_count,
                'nuevo_stock': producto.stock,
                'mensaje': f'Producto agregado exitosamente. Stock actualizado: {producto.stock}'
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'error': f'Error interno: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

# ========== VISTAS ADICIONALES ==========

@login_required
def eliminar_detalle(request, detalle_id):
    """
    Eliminar un producto del pedido
    """
    try:
        detalle = get_object_or_404(DetallePedido, id=detalle_id, pedido__usuario=request.user)
        
        # Restaurar stock
        producto = detalle.producto
        producto.stock += detalle.cantidad
        producto.save()
        
        # Eliminar detalle
        pedido = detalle.pedido
        detalle.delete()
        
        # Recalcular total
        total_pedido = DetallePedido.objects.filter(
            pedido=pedido
        ).aggregate(total=Sum('subtotal'))['total'] or 0
        pedido.total = total_pedido
        pedido.save()
        
        messages.success(request, 'Producto eliminado del pedido')
        
    except Exception as e:
        messages.error(request, f'Error al eliminar: {str(e)}')
    
    return redirect('mi_pedido')

@login_required
def actualizar_cantidad(request, detalle_id):
    """
    Actualizar cantidad de un producto en el pedido
    """
    if request.method == 'POST':
        try:
            detalle = get_object_or_404(DetallePedido, id=detalle_id, pedido__usuario=request.user)
            nueva_cantidad = int(request.POST.get('cantidad', 1))
            
            if nueva_cantidad <= 0:
                messages.error(request, 'La cantidad debe ser mayor a 0')
                return redirect('mi_pedido')
            
            # Calcular diferencia
            diferencia = nueva_cantidad - detalle.cantidad
            
            # Verificar stock
            if detalle.producto.stock < diferencia:
                messages.error(request, f'Stock insuficiente. Solo hay {detalle.producto.stock} unidades disponibles')
                return redirect('mi_pedido')
            
            # Actualizar stock
            detalle.producto.stock -= diferencia
            detalle.producto.save()
            
            # Actualizar detalle
            detalle.cantidad = nueva_cantidad
            detalle.save()  # Recalcula subtotal automáticamente
            
            # Recalcular total del pedido
            pedido = detalle.pedido
            total_pedido = DetallePedido.objects.filter(
                pedido=pedido
            ).aggregate(total=Sum('subtotal'))['total'] or 0
            pedido.total = total_pedido
            pedido.save()
            
            messages.success(request, 'Cantidad actualizada correctamente')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
    
    return redirect('mi_pedido')