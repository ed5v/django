import re
import json
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.timezone import datetime
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages  # Para usar mensajes flash
from django.contrib.auth.decorators import login_required
from .models import Categoria, Producto, Pedido, ItemPedido
from .models import Receta, Ingrediente, Paso, FotoReceta, InfoNutricional
from .forms import (
    RecetaForm,
    IngredientesFormSet,
    PasosFormSet,
    FotosFormSet,
    NutricionalFormSet
)
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
def lista_recetas(request):
    recetas = Receta.objects.all().order_by("-created_at")
    return render(request, "recetas/lista_recetas.html", {"recetas": recetas})

@login_required
def detalle_receta(request, pk):
    receta = Receta.objects.get(pk=pk)
    return render(request, "recetas/detalle_receta.html", {"receta": receta})

@login_required
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
def eliminar_receta(request, pk):
    receta = Receta.objects.get(pk=pk)

    if request.method == "POST":
        receta.delete()
        messages.success(request, "Receta eliminada")
        return redirect("lista_recetas")

    return render(request, "recetas/eliminar_receta.html", {"receta": receta})

@login_required
def AUDITORIA (request):
    return render(request,'AUDITORIA.html')   

@login_required
def CAJA (request):
    return render(request,'CAJA.html')

@login_required
def CUENTA (request):
    return render(request,'CUENTA.html')

def INDEX (request):
    return render(request,'index.html')  

def INICIO (request):
    return render(request,'INICIO.html')   

@login_required
def INVENTARIO (request):
    return render(request,'INVENTARIO.html')   

def ORDEN (request):
    categorias=Categoria.objects.prefetch_related('producto_set')
    return render(request,'ORDEN.html',{'categorias':categorias})   

def menu_view(request):
    categorias = Categoria.objects.prefetch_related('producto_set')
    return render(request, 'menu.html', {'categorias': categorias})

def agregar_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        pedido, _ = Pedido.objects.get_or_create(numero_cliente=data['numero_cliente'])
        producto = Producto.objects.get(id=data['producto_id'])
        item = ItemPedido.objects.create(
            pedido=pedido,
            producto=producto,
            observaciones=data.get('observaciones', ''),
            cantidad=data.get('cantidad', 1)
        )
        return JsonResponse({'status': 'ok'})

def obtener_ticket(request, numero_cliente):
    pedido = Pedido.objects.filter(numero_cliente=numero_cliente).last()
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
            usuario = form.cleaned_data['username']
            contrasena = form.cleaned_data['password']
            user = authenticate(username=usuario, password=contrasena)

            if user:
                login(request, user)
                messages.success(request, f"Bienvenido {usuario}")
                return redirect("INICIO")
        messages.error(request, "Usuario o contraseña inválidos")

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
