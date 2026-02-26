# pedidos/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum

from .models import Pedido, DetallePedido
from Productos.models import Producto


@login_required
def mi_pedido_funcion(request):
    try:
        pedido = Pedido.objects.filter(usuario=request.user, estado='PENDIENTE').first()
        detalles = pedido.detalles.all() if pedido else []
        return render(request, "pedidos/Ordenes.html", {'pedido': pedido, 'detalles': detalles})
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return render(request, "pedidos/Ordenes.html", {'pedido': None, 'detalles': []})


@login_required
def confirmar_pedido(request):
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        try:
            pedido = Pedido.objects.get(usuario=request.user, estado='PENDIENTE')
            if not pedido.detalles.exists():
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'Carrito vacío'})
                messages.error(request, 'Tu carrito está vacío.')
                return redirect('mi_pedido')
            pedido.estado = 'CONFIRMADO'
            pedido.save()
            if is_ajax:
                return JsonResponse({'success': True})
            messages.success(request, '¡Pedido confirmado!')
            return redirect('mi_pedido')
        except Pedido.DoesNotExist:
            if is_ajax:
                return JsonResponse({'success': False, 'error': 'No hay pedido activo'})
            messages.error(request, 'No tienes un pedido activo.')
            return redirect('mi_pedido')
    return redirect('mi_pedido')


@login_required
def agregar_producto_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'})
    try:
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', '1'))
        if not producto_id or cantidad <= 0:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'})
        producto = Producto.objects.get(codigo=producto_id)
        if producto.stock < cantidad:
            return JsonResponse({'success': False, 'error': f'Stock insuficiente. Solo hay {producto.stock}.', 'nuevo_stock': producto.stock})
        pedido, _ = Pedido.objects.get_or_create(usuario=request.user, estado='PENDIENTE', defaults={'total': 0})
        detalle = pedido.detalles.filter(producto=producto).first()
        if detalle:
            nueva_cantidad = detalle.cantidad + cantidad
            if producto.stock < nueva_cantidad:
                return JsonResponse({'success': False, 'error': f'Stock insuficiente.', 'nuevo_stock': producto.stock})
            detalle.cantidad = nueva_cantidad
            detalle.save()
        else:
            DetallePedido.objects.create(pedido=pedido, producto=producto, cantidad=cantidad)
        producto.stock -= cantidad
        producto.save()
        pedido.total = pedido.detalles.aggregate(t=Sum('subtotal'))['t'] or 0
        pedido.save()
        carrito_count = pedido.detalles.aggregate(t=Sum('cantidad'))['t'] or 0
        return JsonResponse({'success': True, 'carrito_count': carrito_count, 'nuevo_stock': producto.stock})
    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Producto no encontrado'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def eliminar_detalle(request, detalle_id):
    try:
        detalle = get_object_or_404(DetallePedido, id=detalle_id, pedido__usuario=request.user)
        detalle.producto.stock += detalle.cantidad
        detalle.producto.save()
        pedido = detalle.pedido
        detalle.delete()
        pedido.total = pedido.detalles.aggregate(t=Sum('subtotal'))['t'] or 0
        pedido.save()
        messages.success(request, 'Producto eliminado')
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    return redirect('mi_pedido')


@login_required
def actualizar_cantidad(request, detalle_id):
    if request.method == 'POST':
        try:
            detalle = get_object_or_404(DetallePedido, id=detalle_id, pedido__usuario=request.user)
            nueva_cantidad = int(request.POST.get('cantidad', 1))
            if nueva_cantidad <= 0:
                messages.error(request, 'La cantidad debe ser mayor a 0')
                return redirect('mi_pedido')
            diferencia = nueva_cantidad - detalle.cantidad
            if detalle.producto.stock < diferencia:
                messages.error(request, f'Stock insuficiente. Disponible: {detalle.producto.stock}')
                return redirect('mi_pedido')
            detalle.producto.stock -= diferencia
            detalle.producto.save()
            detalle.cantidad = nueva_cantidad
            detalle.save()
            pedido = detalle.pedido
            pedido.total = pedido.detalles.aggregate(t=Sum('subtotal'))['t'] or 0
            pedido.save()
            messages.success(request, 'Cantidad actualizada')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
    return redirect('mi_pedido')


@login_required
def hacer_pedido(request):
    return redirect('mi_pedido')


@login_required
def detalle_pedido_admin(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    items = []
    for d in pedido.detalles.select_related('producto').all():
        imagen_url = None
        if hasattr(d.producto, 'imagen') and d.producto.imagen:
            try:
                imagen_url = d.producto.imagen.url
            except Exception:
                pass
        items.append({
            'producto': d.producto.nombre,
            'cantidad': d.cantidad,
            'precio_unit': float(d.producto.precio),
            'subtotal': float(d.subtotal),
            'imagen': imagen_url,
        })
    try:
        estado_str = pedido.get_estado_display()
    except Exception:
        estado_str = pedido.estado
    return JsonResponse({
        'pedido_id': pedido.id,
        'cliente': pedido.usuario.username,
        'fecha': pedido.fecha.strftime('%d/%m/%Y %H:%M'),
        'estado': estado_str,
        'total': float(pedido.total),
        'items': items,
    })