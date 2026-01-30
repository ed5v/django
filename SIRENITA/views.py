import re
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.timezone import datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages  # Para usar mensajes flash
from django.contrib.auth.decorators import login_required
from .models import Categoria, Producto, Pedido, ItemPedido
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
        return JsonResponse({'items': []})

    items = pedido.items.all()
    items_data = [{
        'producto': item.producto.nombre,
        'cantidad': item.cantidad,
        'precio': str(item.producto.precio),
        'observaciones': item.observaciones
    } for item in items]

    return JsonResponse({'items': items_data})

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
