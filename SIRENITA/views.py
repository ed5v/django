import re
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.timezone import datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages  # Para usar mensajes flash
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Sum, Count, Q, F, DecimalField, Value
from django.db.models.functions import TruncDate, Coalesce
from .models import Categoria, Producto, Pedido, ItemPedido, RegistroPedido, Cupon, Mesa
from .models import Receta, Ingrediente, PasoPreparacion, Foto, Nutricional
from .payment_service import PaymentService
from .forms import (
    RecetaForm,
    IngredientesFormSet,
    PasosFormSet,
    FotosFormSet,
    NutricionalFormSet
)
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .decorators import admin_required
#from django.http import HttpResponse

layout= """
<h1> BIENVENIDO  </h1>
<hr/>
<ul>
    <li>
        <a href="/AUDITORIA">AUDITORIA</a>
    </li>
    <li>
        <a href="/CAJA">CAJA</a>
    </li>
    <li>
    <a href="/CUENTA">CUENTA</a>
    </li>
    <li>
        <a href="/INDEX">INDEX</a>
    </li>
    <li>
        <a href="/INICIO">INICIO</a>
    </li>
    <li>
        <a href="/INVENTARIO">INVENTARIO</a>
    </li>
    <li>
        <a href="/ORDEN">ORDEN</a>
    </li>

</ul>
<hr/>
"""



"""def index(request):
    return render(request,'index.html')"""

@login_required
@admin_required
def lista_recetas(request):
    recetas = Receta.objects.all().order_by("-created_at")
    return render(request, "recetas/lista_recetas.html", {"recetas": recetas})


@login_required
@admin_required
def detalle_receta(request, pk):
    receta = Receta.objects.get(pk=pk)
    return render(request, "recetas/detalle_receta.html", {"receta": receta})


@login_required
def CUENTA(request):
    """Vista de cuentas pendientes - muestra los tickets pendientes de pago con items solicitados.
    - Usuarios normales ven solo sus tickets.
    - El usuario 'pc' ve todos los tickets.
    """
    # Base queryset
    base_qs = Pedido.objects.filter(
        estado_pago='PENDIENTE_DE_PAGO',
        items__solicitado=True
    )

    # DEBUG: Log para verificar el usuario actual
    print(f"[DEBUG CUENTA] Usuario logueado: {request.user.username} (id={request.user.id})")
    
    if request.user.username == 'pc':
        tickets_qs = base_qs
        print(f"[DEBUG CUENTA] Usuario 'pc' - mostrando TODOS los tickets")
    else:
        tickets_qs = base_qs.filter(usuario=request.user)
        print(f"[DEBUG CUENTA] Usuario '{request.user.username}' - filtrando por usuario")

    tickets_qs = tickets_qs.distinct().select_related('usuario', 'cupon_aplicado').prefetch_related('items__producto__categoria').order_by('-creado')
    
    # DEBUG: Log para ver qué tickets se van a mostrar
    print(f"[DEBUG CUENTA] Total de tickets a mostrar: {tickets_qs.count()}")
    for t in tickets_qs:
        print(f"[DEBUG CUENTA]   - Ticket #{t.id} (usuario: {t.usuario.username})")

    tickets_info = []
    for ticket in tickets_qs:
        total_original = ticket.total()
        total_final = ticket.total_con_descuento()

        items_solicitados = []
        for item in ticket.items.filter(solicitado=True):
            items_solicitados.append({
                'item': item,
                'pagado': hasattr(item, 'pagado_individual') and item.pagado_individual,
            })

        tickets_info.append({
            'ticket': ticket,
            'total_original': total_original,
            'total_final': total_final,
            'tiene_cupon': ticket.cupon_aplicado is not None,
            'cupon': ticket.cupon_aplicado,
            'items_solicitados': items_solicitados,
        })

    return render(request, 'CUENTA.html', {
        'tickets_pendientes': tickets_info
    })

@login_required
@admin_required
def crear_receta(request):
    receta = Receta()

    if request.method == "POST":
        form = RecetaForm(request.POST)
        ingredientes_formset = IngredientesFormSet(request.POST, instance=receta)
        pasos_formset = PasosFormSet(request.POST, instance=receta)
        fotos_formset = FotosFormSet(request.POST, request.FILES, instance=receta)
        nutricion_formset = NutricionalFormSet(request.POST, instance=receta)

        if (
            form.is_valid()
            and ingredientes_formset.is_valid()
            and pasos_formset.is_valid()
            and fotos_formset.is_valid()
            and nutricion_formset.is_valid()
        ):
            receta = form.save()

            # Se asigna la receta a todos los formsets
            ingredientes_formset.instance = receta
            pasos_formset.instance = receta
            fotos_formset.instance = receta
            nutricion_formset.instance = receta

            ingredientes_formset.save()
            pasos_formset.save()
            fotos_formset.save()
            nutricion_formset.save()

            messages.success(request, "Receta creada correctamente")
            return redirect("lista_recetas")

    else:
        form = RecetaForm()
        ingredientes_formset = IngredientesFormSet(instance=receta)
        pasos_formset = PasosFormSet(instance=receta)
        fotos_formset = FotosFormSet(instance=receta)
        nutricion_formset = NutricionalFormSet(instance=receta)

    return render(request, "recetas/crear_receta.html", {
        "form": form,
        "ingredientes_formset": ingredientes_formset,
        "pasos_formset": pasos_formset,
        "fotos_formset": fotos_formset,
        "nutricion_formset": nutricion_formset,
    })

@login_required
@admin_required
def editar_receta(request, pk):
    receta = Receta.objects.get(pk=pk)

    if request.method == "POST":
        form = RecetaForm(request.POST, instance=receta)
        ingredientes_formset = IngredientesFormSet(request.POST, instance=receta)
        pasos_formset = PasosFormSet(request.POST, instance=receta)
        fotos_formset = FotosFormSet(request.POST, request.FILES, instance=receta)
        nutricion_formset = NutricionalFormSet(request.POST, instance=receta)

        if (
            form.is_valid()
            and ingredientes_formset.is_valid()
            and pasos_formset.is_valid()
            and fotos_formset.is_valid()
            and nutricion_formset.is_valid()
        ):
            form.save()
            ingredientes_formset.save()
            pasos_formset.save()
            fotos_formset.save()
            nutricion_formset.save()

            messages.success(request, "Receta actualizada correctamente")
            return redirect("lista_recetas")

    else:
        form = RecetaForm(instance=receta)
        ingredientes_formset = IngredientesFormSet(instance=receta)
        pasos_formset = PasosFormSet(instance=receta)
        fotos_formset = FotosFormSet(instance=receta)
        nutricion_formset = NutricionalFormSet(instance=receta)

    return render(request, "recetas/editar_receta.html", {
        "form": form,
        "ingredientes_formset": ingredientes_formset,
        "pasos_formset": pasos_formset,
        "fotos_formset": fotos_formset,
        "nutricion_formset": nutricion_formset,
        "receta": receta,
    })

@login_required
@admin_required
def eliminar_receta(request, pk):
    receta = Receta.objects.get(pk=pk)

    if request.method == "POST":
        receta.delete()
        messages.success(request, "Receta eliminada")
        return redirect("lista_recetas")

    return render(request, "recetas/eliminar_receta.html", {"receta": receta})

@login_required
@admin_required
def AUDITORIA (request):
    return render(request,'AUDITORIA.html')   

@login_required
@admin_required
def CAJA (request):
    return render(request,'CAJA.html')

#@login_required
#@admin_required
def CUENTA(request):
    """Vista de cuentas pendientes - todos los tickets pendientes de pago con items solicitados"""
    mesa_busqueda = request.GET.get('mesa', '').strip()

    # Obtener todos los tickets que tienen items solicitados y están pendientes de pago
    tickets_pendientes = Pedido.objects.filter(
        estado_pago='PENDIENTE_DE_PAGO',
        items__solicitado=True
    )

    if mesa_busqueda:
        try:
            tickets_pendientes = tickets_pendientes.filter(mesa=int(mesa_busqueda))
        except ValueError:
            tickets_pendientes = tickets_pendientes.none()

    tickets_pendientes = tickets_pendientes.distinct().select_related('usuario', 'cupon_aplicado').prefetch_related('items__producto__categoria').order_by('-creado')
    
    # Calcular información de cada ticket
    tickets_info = []
    for ticket in tickets_pendientes:
        total_original = ticket.total()
        total_final = ticket.total_con_descuento()
        
        # Obtener items solicitados con estado de pago individual
        items_solicitados = []
        for item in ticket.items.filter(solicitado=True):
            items_solicitados.append({
                'item': item,
                'pagado': hasattr(item, 'pagado_individual') and item.pagado_individual,
            })
        
        tickets_info.append({
            'ticket': ticket,
            'total_original': total_original,
            'total_final': total_final,
            'tiene_cupon': ticket.cupon_aplicado is not None,
            'cupon': ticket.cupon_aplicado,
            'items_solicitados': items_solicitados,
        })
    
    return render(request, 'CUENTA.html', {
        'tickets_pendientes': tickets_info,
        'mesa_busqueda': mesa_busqueda,
    })

def INDEX (request):
    return render(request,'index.html')  

def INICIO (request):
    return render(request,'INICIO.html')   

@login_required
def SEGUIMIENTO(request):
    # Total de ventas (solo pedidos completados)
    total_ventas = Pedido.objects.filter(completado=True).aggregate(
        total=Sum(F('items__cantidad') * F('items__producto__precio'), output_field=DecimalField())
    )['total'] or 0
    
    # Ventas por usuario
    ventas_por_usuario = Pedido.objects.filter(completado=True).values(
        'usuario__username'
    ).annotate(
        total=Sum(F('items__cantidad') * F('items__producto__precio'), output_field=DecimalField()),
        num_pedidos=Count('id')
    ).order_by('-total')
    
    # Productos más vendidos
    productos_mas_vendidos = ItemPedido.objects.filter(
        pedido__completado=True
    ).values(
        'producto__nombre'
    ).annotate(
        cantidad_total=Sum('cantidad'),
        ingresos=Sum(F('cantidad') * F('producto__precio'), output_field=DecimalField())
    ).order_by('-cantidad_total')[:10]
    
    # Historial de ventas (últimos 30 días)
    historial_ventas = Pedido.objects.filter(
        completado=True
    ).annotate(
        fecha=TruncDate('creado')
    ).values('fecha').annotate(
        total_dia=Sum(F('items__cantidad') * F('items__producto__precio'), output_field=DecimalField()),
        num_pedidos=Count('id')
    ).order_by('-fecha')[:30]
    
    # Pedidos pendientes (información en tiempo real)
    pedidos_pendientes = Pedido.objects.filter(completado=False).count()
    
    # Pedidos completados hoy
    from django.utils import timezone
    hoy = timezone.now().date()
    pedidos_hoy = Pedido.objects.filter(completado=True, creado__date=hoy).count()
    
    # Tickets pagados recientes (últimos 50)
    tickets_pagados = Pedido.objects.filter(
        estado_pago='PAGADO'
    ).select_related('usuario', 'cupon_aplicado').prefetch_related('items__producto').order_by('-fecha_pago')[:50]
    
    context = {
        'total_ventas': total_ventas,
        'ventas_por_usuario': ventas_por_usuario,
        'productos_mas_vendidos': productos_mas_vendidos,
        'historial_ventas': historial_ventas,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_hoy': pedidos_hoy,
        'tickets_pagados': tickets_pagados,
    }
    
    return render(request, 'SEGUIMIENTO.html', context)

@login_required
@admin_required
def INVENTARIO (request):
    return render(request,'INVENTARIO.html')   

@login_required
def crear_ticket(request):
    mesa = request.POST.get('mesa') if request.method == 'POST' else request.GET.get('mesa')
    personas = request.POST.get('personas') if request.method == 'POST' else request.GET.get('personas')

    mesa_valor = None
    personas_valor = None

    if mesa not in (None, ''):
        try:
            mesa_valor = int(mesa)
        except (TypeError, ValueError):
            mesa_valor = None

    if personas not in (None, ''):
        try:
            personas_valor = int(personas)
            if personas_valor <= 0:
                personas_valor = None
        except (TypeError, ValueError):
            personas_valor = None

    pedido = Pedido.objects.create(
        usuario=request.user,
        mesa=mesa_valor,
        personas=personas_valor,
    )
    pedido.numero_cliente = pedido.id
    pedido.save()
    return redirect(f'/ORDEN/?ticket_id={pedido.id}')


@login_required
def cancelar_ticket(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    if not request.user.is_superuser:
        return JsonResponse({'status': 'error', 'message': 'Solo superusuarios pueden cancelar tickets'}, status=403)

    try:
        data = json.loads(request.body)
        ticket_id = data.get('ticket_id')

        qs = Pedido.objects.filter(id=ticket_id, completado=False)
        if not request.user.is_staff:
            qs = qs.filter(usuario=request.user)

        pedido = qs.first()
        if not pedido:
            return JsonResponse({'status': 'error', 'message': 'Ticket no encontrado'}, status=404)

        if pedido.items.filter(solicitado=True).exists() or RegistroPedido.objects.filter(ticket=pedido).exists():
            return JsonResponse(
                {'status': 'error', 'message': 'No se puede cancelar: el ticket ya fue solicitado'},
                status=400
            )

        pedido.delete()
        return JsonResponse({'status': 'ok', 'message': 'Ticket cancelado correctamente'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@never_cache
def ORDEN(request):
    ticket_id = request.GET.get('ticket_id')
    mesa_busqueda = request.GET.get('mesa', '').strip()
    ticket_actual = None
    
    if ticket_id:
        qs = Pedido.objects.filter(id=ticket_id)
        if not request.user.is_staff:
            qs = qs.filter(usuario=request.user)
        ticket_actual = qs.first()

    total_ticket_expr = Sum(
        F('items__cantidad') * F('items__producto__precio'),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )
    total_ticket_annotated = Coalesce(
        total_ticket_expr,
        Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))
    )

    tickets_abiertos = Pedido.objects.filter(completado=False)
    if not request.user.is_staff:
        tickets_abiertos = tickets_abiertos.filter(usuario=request.user)

    if mesa_busqueda:
        try:
            tickets_abiertos = tickets_abiertos.filter(mesa=int(mesa_busqueda))
        except ValueError:
            tickets_abiertos = tickets_abiertos.none()

    tickets_abiertos = (
        tickets_abiertos
        .annotate(total_ticket=total_ticket_annotated)
        .order_by('-creado', '-id')
    )

    categorias = Categoria.objects.prefetch_related('productos')
    mesas_disponibles = Mesa.objects.order_by('mesa').values_list('mesa', flat=True)
    return render(request, 'ORDEN.html', {
        'categorias': categorias,
        'ticket_actual': ticket_actual,
        'tickets_abiertos': tickets_abiertos,
        'mesa_busqueda': mesa_busqueda,
        'mesas_disponibles': mesas_disponibles,
    })


@login_required
def actualizar_datos_ticket(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    ticket_id = request.POST.get('ticket_id')
    mesa = request.POST.get('mesa')
    personas = request.POST.get('personas')
    observaciones = (request.POST.get('observaciones') or '').strip()

    qs = Pedido.objects.filter(id=ticket_id, completado=False)
    if not request.user.is_staff:
        qs = qs.filter(usuario=request.user)

    pedido = qs.first()
    if not pedido:
        messages.error(request, 'Ticket no encontrado o sin permisos.')
        return redirect('ORDEN')

    try:
        mesa_valor = int(mesa)
    except (TypeError, ValueError):
        messages.error(request, 'La mesa debe ser un número válido.')
        return redirect(f'/ORDEN/?ticket_id={pedido.id}')

    if not Mesa.objects.filter(mesa=mesa_valor).exists():
        messages.error(request, 'La mesa seleccionada no existe en el catálogo.')
        return redirect(f'/ORDEN/?ticket_id={pedido.id}')

    try:
        personas_valor = int(personas)
        if personas_valor <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        messages.error(request, 'El campo personas debe ser un número entero mayor a 0.')
        return redirect(f'/ORDEN/?ticket_id={pedido.id}')

    pedido.mesa = mesa_valor
    pedido.personas = personas_valor
    pedido.observaciones = observaciones
    pedido.save(update_fields=['mesa', 'personas', 'observaciones'])

    messages.success(request, 'Datos de la orden actualizados correctamente.')
    return redirect(f'/ORDEN/?ticket_id={pedido.id}')

def menu_view(request):
    categorias = Categoria.objects.prefetch_related('productos')
    return render(request, 'menu.html', {'categorias': categorias})

@login_required
def agregar_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket_id = data.get('ticket_id')
            
            qs = Pedido.objects.filter(id=ticket_id)
            if not request.user.is_staff:
                qs = qs.filter(usuario=request.user)
            
            pedido = qs.first()
            if not pedido:
                return JsonResponse({'status': 'error', 'message': 'Ticket no encontrado'}, status=404)

            producto = get_object_or_404(Producto, id=data['producto_id'])
            
            item = ItemPedido.objects.create(
                pedido=pedido,
                producto=producto,
                observaciones=data.get('observaciones', ''),
                cantidad=data.get('cantidad', 1)
            )
            return JsonResponse({
                'status': 'ok',
                'item_id': item.id,
                'cantidad': item.cantidad,
                'observaciones': item.observaciones or '',
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def editar_item_ticket(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')
        cantidad = data.get('cantidad')
        observaciones = (data.get('observaciones') or '').strip()

        qs = ItemPedido.objects.select_related('pedido', 'producto').filter(id=item_id, solicitado=False)
        if not request.user.is_staff:
            qs = qs.filter(pedido__usuario=request.user)

        item = qs.first()
        if not item:
            return JsonResponse({'status': 'error', 'message': 'Item no encontrado o no editable'}, status=404)

        if cantidad in (None, ''):
            cantidad_valor = item.cantidad
        else:
            try:
                cantidad_valor = int(cantidad)
                if cantidad_valor <= 0:
                    raise ValueError()
            except (TypeError, ValueError):
                return JsonResponse({'status': 'error', 'message': 'La cantidad debe ser un entero mayor a 0'}, status=400)

        item.cantidad = cantidad_valor
        item.observaciones = observaciones
        item.save(update_fields=['cantidad', 'observaciones'])

        return JsonResponse({
            'status': 'ok',
            'item_id': item.id,
            'cantidad': item.cantidad,
            'observaciones': item.observaciones or '',
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def eliminar_item_ticket(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        item_id = data.get('item_id')

        qs = ItemPedido.objects.select_related('pedido').filter(id=item_id, solicitado=False)
        if not request.user.is_staff:
            qs = qs.filter(pedido__usuario=request.user)

        item = qs.first()
        if not item:
            return JsonResponse({'status': 'error', 'message': 'Item no encontrado o no editable'}, status=404)

        item.delete()
        return JsonResponse({'status': 'ok', 'item_id': item_id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def obtener_ticket(request, numero_cliente):
    qs = Pedido.objects.filter(id=numero_cliente)
    if not request.user.is_staff:
        qs = qs.filter(usuario=request.user)

    pedido = qs.first()
    if not pedido:
        return JsonResponse({'items_solicitados': [], 'items_nuevos': []})

    # Separar items solicitados de items nuevos
    items_solicitados = pedido.items.filter(solicitado=True)
    items_nuevos = pedido.items.filter(solicitado=False)
    
    items_solicitados_data = [{
        'id': item.id,
        'producto': item.producto.nombre,
        'cantidad': item.cantidad,
        'precio': str(item.producto.precio),
        'observaciones': item.observaciones,
        'solicitado': True
    } for item in items_solicitados]
    
    items_nuevos_data = [{
        'id': item.id,
        'producto': item.producto.nombre,
        'cantidad': item.cantidad,
        'precio': str(item.producto.precio),
        'observaciones': item.observaciones,
        'solicitado': False
    } for item in items_nuevos]

    return JsonResponse({
        'items_solicitados': items_solicitados_data,
        'items_nuevos': items_nuevos_data
    })

@login_required
def solicitar_pedido(request):
    """Registra los items del pedido en la tabla de registro para gestión de pagos y envía a impresoras por categoría"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket_id = data.get('ticket_id')
            
            # Verificar permisos
            qs = Pedido.objects.filter(id=ticket_id)
            if not request.user.is_staff:
                qs = qs.filter(usuario=request.user)
            
            pedido = qs.first()
            if not pedido:
                return JsonResponse({'status': 'error', 'message': 'Ticket no encontrado'}, status=404)
            
            # Obtener solo los items NO solicitados
            items_no_solicitados = pedido.items.filter(solicitado=False)
            
            if not items_no_solicitados.exists():
                return JsonResponse({'status': 'error', 'message': 'No hay items nuevos para solicitar'}, status=400)
            
            # Registrar todos los items no solicitados en la tabla de registro
            items_registrados = 0
            items_comida = []
            items_bebidas = []
            
            for item in items_no_solicitados:
                # Crear registro
                RegistroPedido.objects.create(
                    usuario=request.user,
                    ticket=pedido,
                    producto=item.producto,
                    categoria=item.producto.categoria,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio,
                    subtotal=item.subtotal(),
                    observaciones=item.observaciones
                )
                
                # Marcar como solicitado
                item.solicitado = True
                item.save()
                
                items_registrados += 1
                
                # Clasificar por categoría para impresión
                categoria_nombre = item.producto.categoria.nombre.lower()
                item_info = {
                    'producto': item.producto.nombre,
                    'cantidad': item.cantidad,
                    'observaciones': item.observaciones or ''
                }
                
                if 'comida' in categoria_nombre or 'plato' in categoria_nombre or 'entrada' in categoria_nombre:
                    items_comida.append(item_info)
                elif 'bebida' in categoria_nombre or 'drink' in categoria_nombre:
                    items_bebidas.append(item_info)
                else:
                    # Por defecto va a comida
                    items_comida.append(item_info)
            
            # Simular envío a impresoras (aquí deberías integrar tu lógica real de impresión)
            mensaje_impresion = ""
            if items_comida:
                mensaje_impresion += f"✓ {len(items_comida)} items enviados a IMPRESORA 01 (Cocina)\n"
                # TODO: Aquí agregar código para enviar a impresora 01
                # print_to_kitchen(items_comida, ticket_id)
                
            if items_bebidas:
                mensaje_impresion += f"✓ {len(items_bebidas)} items enviados a IMPRESORA 02 (Bar)"
                # TODO: Aquí agregar código para enviar a impresora 02
                # print_to_bar(items_bebidas, ticket_id)
            
            return JsonResponse({
                'status': 'ok',
                'message': f'Pedido solicitado exitosamente.\n{mensaje_impresion}',
                'items_registrados': items_registrados,
                'items_comida': len(items_comida),
                'items_bebidas': len(items_bebidas)
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=400)

@login_required
@admin_required
def listar_registros_pedidos(request):
    """Muestra todos los registros de pedidos para gestión de pagos"""
    if request.user.is_staff:
        registros = RegistroPedido.objects.select_related(
            'usuario', 'ticket', 'producto', 'categoria'
        ).all()
    else:
        registros = RegistroPedido.objects.filter(
            usuario=request.user
        ).select_related('ticket', 'producto', 'categoria')
    
    # Agrupar por ticket
    tickets_dict = {}
    for registro in registros:
        ticket_id = registro.ticket.id
        if ticket_id not in tickets_dict:
            tickets_dict[ticket_id] = {
                'ticket': registro.ticket,
                'usuario': registro.usuario,
                'fecha': registro.fecha,
                'items': [],
                'total': 0,
                'pagado': True
            }
        tickets_dict[ticket_id]['items'].append(registro)
        tickets_dict[ticket_id]['total'] += registro.subtotal
        if not registro.pagado:
            tickets_dict[ticket_id]['pagado'] = False
    
    context = {
        'tickets': tickets_dict.values()
    }
    
    return render(request, 'registro_pedidos.html', context)

@login_required
def marcar_pagado(request, registro_id):
    """Marca un registro de pedido como pagado"""
    if request.method == 'POST':
        try:
            registro = get_object_or_404(RegistroPedido, id=registro_id)
            
            if not request.user.is_staff and registro.usuario != request.user:
                return JsonResponse({'status': 'error', 'message': 'Sin permisos'}, status=403)
            
            registro.pagado = True
            registro.save()
            
            ticket_completo = not RegistroPedido.objects.filter(
                ticket=registro.ticket, pagado=False
            ).exists()
            
            if ticket_completo:
                from django.utils import timezone
                registro.ticket.completado = True
                registro.ticket.estado_pago = 'PAGADO'
                registro.ticket.fecha_pago = timezone.now()
                registro.ticket.save()
            
            return JsonResponse({
                'status': 'ok',
                'message': 'Registro marcado como pagado',
                'ticket_completo': ticket_completo
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

    items = [{
        'producto': item.producto.nombre,
        'cantidad': item.cantidad,
        'observaciones': item.observaciones,
        'precio': item.producto.precio
    } for item in pedido.items.all()]

    return JsonResponse({'items': items})


def save_articulo(request):
    articulo=Article(
        title =title,
        content=content,
        public=public
    )
    articulo.save()
    return HttpResponse(f"Articulo creado: <strong>{articulo.title}")
 
 
def create_articulo(request):
    return render(request, 'create_article.html')

"""def hello_there(request, name):
#     print(request.build_absolute_uri()) #optional
#    return render(
#        request,
#        'SIRENITA/INICIO.HTML',
#        {
#            'name': name,
#            'date': datetime.now()
#        }
#    )"""



from django.shortcuts import render

def boton(request):
    imagen='logo.png'
    texto= 'texto del botón'
    return render(request, 'ORDEN.html', {'imagen': imagen, 'texto': texto})

#def tabla_menu(request):
    #return render(request, 'SIRENITA/tabla.html')

def agregar_orden(request, numero):
    if numero==1:
        print("Acción 1 ejecutada")
    elif numero==2:
        print("Acción 2 ejecutada")
    elif numero==3:
        print("Acción 3 ejecutada")
    return redirect('tabla')

def logout_request(request):
    logout(request)
    messages.info(request, "Sesión finalizada")
    return redirect("INICIO")

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirigir a la página solicitada originalmente (parámetro 'next')
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect("INICIO")

        return render(request, "login.html", {
            "form": form,
            "error": "Usuario o contraseña incorrectos",
            "next": request.GET.get('next', '')
        })

    form = AuthenticationForm()
    next_url = request.GET.get('next', '')
    return render(request, "login.html", {"form": form, "next": next_url})


def crear_receta(request):
    receta = Receta()

    if request.method == "POST":
        form = RecetaForm(request.POST)
        ingredientes_formset = IngredientesFormSet(request.POST, instance=receta)
        pasos_formset = PasosFormSet(request.POST, instance=receta)
        fotos_formset = FotosFormSet(request.POST, request.FILES, instance=receta)
        nutricion_formset = NutricionalFormSet(request.POST, instance=receta)

        if (
            form.is_valid() and
            ingredientes_formset.is_valid() and
            pasos_formset.is_valid() and
            fotos_formset.is_valid() and
            nutricion_formset.is_valid()
        ):
            receta = form.save()
            ingredientes_formset.instance = receta
            pasos_formset.instance = receta
            fotos_formset.instance = receta
            nutricion_formset.instance = receta

            ingredientes_formset.save()
            pasos_formset.save()
            fotos_formset.save()
            nutricion_formset.save()

            return redirect("lista_recetas")  # o donde tú quieras

    else:
        form = RecetaForm()
        ingredientes_formset = IngredientesFormSet(instance=receta)
        pasos_formset = PasosFormSet(instance=receta)
        fotos_formset = FotosFormSet(instance=receta)
        nutricion_formset = NutricionalFormSet(instance=receta)

    return render(request, "recetas/crear_receta.html", {
        "form": form,
        "ingredientes_formset": ingredientes_formset,
        "pasos_formset": pasos_formset,
        "fotos_formset": fotos_formset,
        "nutricion_formset": nutricion_formset,
    })


# ===========================================
#       GESTIÓN DE PAGOS Y CUPONES
# ===========================================

@login_required
@admin_required
def validar_cupon(request):
    """Valida un cupón sin aplicarlo"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            codigo = data.get('codigo', '').strip().upper()
            ticket_id = data.get('ticket_id')
            
            if not codigo:
                return JsonResponse({'valid': False, 'mensaje': 'Código vacío'})
            
            # Buscar cupón
            try:
                cupon = Cupon.objects.get(codigo=codigo)
            except Cupon.DoesNotExist:
                return JsonResponse({'valid': False, 'mensaje': 'Cupón no existe'})
            
            # Validar disponibilidad
            puede_usar, mensaje = cupon.puede_usarse()
            if not puede_usar:
                return JsonResponse({'valid': False, 'mensaje': mensaje})
            
            # Calcular descuento
            ticket = Pedido.objects.get(id=ticket_id)
            total_original = ticket.total()
            descuento = cupon.calcular_descuento(total_original)
            total_final = total_original - descuento
            
            return JsonResponse({
                'valid': True,
                'mensaje': 'Cupón válido',
                'cupon': {
                    'codigo': cupon.codigo,
                    'tipo': cupon.tipo_descuento,
                    'valor': str(cupon.valor),
                    'descuento': str(descuento),
                    'total_final': str(total_final)
                }
            })
            
        except Exception as e:
            return JsonResponse({'valid': False, 'mensaje': f'Error: {str(e)}'})
    
    return JsonResponse({'valid': False, 'mensaje': 'Método no permitido'})


@login_required
@admin_required
def aplicar_cupon(request):
    """Aplica un cupón a un ticket"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            codigo = data.get('codigo', '').strip().upper()
            ticket_id = data.get('ticket_id')
            
            # Obtener ticket y cupón
            ticket = Pedido.objects.get(id=ticket_id)
            cupon = Cupon.objects.get(codigo=codigo)
            
            # Validar cupón
            puede_usar, mensaje = cupon.puede_usarse()
            if not puede_usar:
                return JsonResponse({'success': False, 'mensaje': mensaje})
            
            # Calcular descuento
            total_original = ticket.total()
            descuento = cupon.calcular_descuento(total_original)
            
            # Aplicar cupón
            ticket.cupon_aplicado = cupon
            ticket.descuento_aplicado = descuento
            ticket.save()
            
            # Incrementar usos del cupón
            cupon.usos_actuales += 1
            cupon.save()
            
            return JsonResponse({
                'success': True,
                'mensaje': 'Cupón aplicado correctamente',
                'descuento': str(descuento),
                'total_final': str(total_original - descuento),
                'cupon': {
                    'codigo': cupon.codigo,
                    'tipo': cupon.tipo_descuento,
                    'valor': str(cupon.valor)
                }
            })
            
        except Pedido.DoesNotExist:
            return JsonResponse({'success': False, 'mensaje': 'Ticket no encontrado'})
        except Cupon.DoesNotExist:
            return JsonResponse({'success': False, 'mensaje': 'Cupón no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'mensaje': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'mensaje': 'Método no permitido'})


@login_required
@admin_required
def remover_cupon(request):
    """Remueve un cupón aplicado a un ticket"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket_id = data.get('ticket_id')
            
            ticket = Pedido.objects.get(id=ticket_id)
            
            if ticket.cupon_aplicado:
                # Decrementar usos del cupón
                cupon = ticket.cupon_aplicado
                if cupon.usos_actuales > 0:
                    cupon.usos_actuales -= 1
                    cupon.save()
                
                # Remover cupón del ticket
                ticket.cupon_aplicado = None
                ticket.descuento_aplicado = 0
                ticket.save()
                
                return JsonResponse({
                    'success': True,
                    'mensaje': 'Cupón removido',
                    'total_final': str(ticket.total())
                })
            else:
                return JsonResponse({'success': False, 'mensaje': 'No hay cupón aplicado'})
                
        except Exception as e:
            return JsonResponse({'success': False, 'mensaje': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'mensaje': 'Método no permitido'})


@login_required
@admin_required
def pagar_ticket(request):
    """Procesa el pago completo de un ticket"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ticket_id = data.get('ticket_id')
            metodo_pago = data.get('metodo_pago', 'EFECTIVO')
            
            ticket = Pedido.objects.get(id=ticket_id)
            
            # Verificar que esté pendiente
            if ticket.estado_pago != 'PENDIENTE_DE_PAGO':
                return JsonResponse({'success': False, 'mensaje': 'Ticket ya fue pagado'})
            
            # Calcular monto final
            monto = ticket.total_con_descuento()
            
            # Procesar pago con el servicio de pagos
            payment_service = PaymentService()
            resultado = payment_service.process_payment(
                ticket_id=ticket.id,
                amount=monto,
                method=metodo_pago
            )
            
            if resultado.success:
                # Actualizar ticket
                from django.utils import timezone
                ticket.estado_pago = 'PAGADO'
                ticket.fecha_pago = timezone.now()
                ticket.metodo_pago = metodo_pago
                ticket.completado = True
                ticket.save()
                
                # Crear registro de pago para cada item solicitado
                for item in ticket.items.filter(solicitado=True):
                    RegistroPedido.objects.create(
                        usuario=ticket.usuario,
                        ticket=ticket,
                        producto=item.producto,
                        categoria=item.producto.categoria,
                        cantidad=item.cantidad,
                        precio_unitario=item.producto.precio,
                        subtotal=item.subtotal(),
                        observaciones=item.observaciones,
                        pagado=True
                    )
                
                return JsonResponse({
                    'success': True,
                    'mensaje': 'Pago procesado correctamente',
                    'transaction_id': resultado.transaction_id,
                    'ticket_id': ticket.id
                })
            else:
                return JsonResponse({
                    'success': False,
                    'mensaje': resultado.error or 'Error al procesar el pago'
                })
                
        except Pedido.DoesNotExist:
            return JsonResponse({'success': False, 'mensaje': 'Ticket no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'mensaje': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'mensaje': 'Método no permitido'})


@login_required
@admin_required
def pagar_item_individual(request):
    """Procesa el pago de un item individual de un ticket"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('item_id')
            metodo_pago = data.get('metodo_pago', 'EFECTIVO')
            
            item = ItemPedido.objects.select_related('pedido', 'producto').get(id=item_id)
            ticket = item.pedido
            
            # Verificar que el ticket esté pendiente
            if ticket.estado_pago == 'PAGADO':
                return JsonResponse({'success': False, 'mensaje': 'El ticket completo ya fue pagado'})
            
            # Verificar que el item esté solicitado
            if not item.solicitado:
                return JsonResponse({'success': False, 'mensaje': 'Item no ha sido solicitado'})
            
            # Verificar si ya existe registro de pago para este item
            registro_existente = RegistroPedido.objects.filter(
                ticket=ticket,
                producto=item.producto,
                cantidad=item.cantidad,
                pagado=True
            ).first()
            
            if registro_existente:
                return JsonResponse({'success': False, 'mensaje': 'Este item ya ha sido pagado'})
            
            # Calcular monto del item
            monto = item.subtotal()
            
            # Procesar pago
            payment_service = PaymentService()
            resultado = payment_service.process_payment(
                ticket_id=ticket.id,
                amount=monto,
                method=metodo_pago
            )
            
            if resultado.success:
                # Crear registro de pago individual
                from django.utils import timezone
                RegistroPedido.objects.create(
                    usuario=ticket.usuario,
                    ticket=ticket,
                    producto=item.producto,
                    categoria=item.producto.categoria,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio,
                    subtotal=monto,
                    observaciones=item.observaciones,
                    pagado=True,
                    fecha=timezone.now()
                )
                
                # Verificar si todos los items del ticket están pagados
                items_solicitados = ticket.items.filter(solicitado=True)
                items_pagados = RegistroPedido.objects.filter(
                    ticket=ticket,
                    pagado=True
                ).count()
                
                # Si todos los items están pagados, marcar ticket como pagado
                if items_pagados >= items_solicitados.count():
                    ticket.estado_pago = 'PAGADO'
                    ticket.fecha_pago = timezone.now()
                    ticket.metodo_pago = metodo_pago
                    ticket.completado = True
                    ticket.save()
                
                return JsonResponse({
                    'success': True,
                    'mensaje': f'Item pagado: {item.producto.nombre}',
                    'transaction_id': resultado.transaction_id,
                    'monto': str(monto),
                    'ticket_completo': items_pagados >= items_solicitados.count()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'mensaje': resultado.error or 'Error al procesar el pago'
                })
                
        except ItemPedido.DoesNotExist:
            return JsonResponse({'success': False, 'mensaje': 'Item no encontrado'})
        except Exception as e:
            return JsonResponse({'success': False, 'mensaje': f'Error: {str(e)}'})
    
    return JsonResponse({'success': False, 'mensaje': 'Método no permitido'})

    
#MVC MODELO VISTA CONTROLADOR
#MVT MODELO TEMPLATE VISTA
