import re
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.timezone import datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages  # Para usar mensajes flash
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q, F, DecimalField
from django.db.models.functions import TruncDate
from .models import Categoria, Producto, Pedido, ItemPedido, RegistroPedido
from .models import Receta, Ingrediente, PasoPreparacion, Foto, Nutricional
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

@login_required
@admin_required
def CUENTA (request):
    return render(request,'CUENTA.html')

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
    
    context = {
        'total_ventas': total_ventas,
        'ventas_por_usuario': ventas_por_usuario,
        'productos_mas_vendidos': productos_mas_vendidos,
        'historial_ventas': historial_ventas,
        'pedidos_pendientes': pedidos_pendientes,
        'pedidos_hoy': pedidos_hoy,
    }
    
    return render(request, 'SEGUIMIENTO.html', context)

@login_required
@admin_required
def INVENTARIO (request):
    return render(request,'INVENTARIO.html')   

@login_required
def crear_ticket(request):
    pedido = Pedido.objects.create(usuario=request.user)
    pedido.numero_cliente = pedido.id
    pedido.save()
    return redirect(f'/ORDEN/?ticket_id={pedido.id}')

@login_required
def ORDEN(request):
    ticket_id = request.GET.get('ticket_id')
    ticket_actual = None
    
    if ticket_id:
        qs = Pedido.objects.filter(id=ticket_id)
        if not request.user.is_staff:
            qs = qs.filter(usuario=request.user)
        ticket_actual = qs.first()

    if request.user.is_staff:
        tickets_abiertos = Pedido.objects.filter(completado=False).order_by('-creado')
    else:
        tickets_abiertos = Pedido.objects.filter(usuario=request.user, completado=False).order_by('-creado')

    categorias = Categoria.objects.prefetch_related('productos')
    return render(request, 'ORDEN.html', {
        'categorias': categorias,
        'ticket_actual': ticket_actual,
        'tickets_abiertos': tickets_abiertos
    })

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
            
            ItemPedido.objects.create(
                pedido=pedido,
                producto=producto,
                observaciones=data.get('observaciones', ''),
                cantidad=data.get('cantidad', 1)
            )
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error'}, status=400)

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
                registro.ticket.completado = True
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
                return redirect("INICIO")

        return render(request, "login.html", {
            "form": form,
            "error": "Usuario o contraseña incorrectos"
        })

    form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


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

    
#MVC MODELO VISTA CONTROLADOR
#MVT MODELO TEMPLATE VISTA
