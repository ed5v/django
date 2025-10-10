import re
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.timezone import datetime
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib
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

def AUDITORIA (request):
    return render(request,'AUDITORIA.html')   

def CAJA (request):
    return render(request,'CAJA.html')

def CUENTA (request):
    return render(request,'CUENTA.html')

def INDEX (request):
    return render(request,'index.html')  

def INICIO (request):
    return render(request,'INICIO.html')   

def INVENTARIO (request):
    return render(request,'INVENTARIO.html')   

def ORDEN (request):
    return render(request,'ORDEN.html')   

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
    return render(request, 'orden.html', {'imagen': imagen, 'texto': texto})

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
    return redirect("INICIO.html")

def login_request(request):

    if request.method=="POST":
        form= AuthenticationForm(request, data=request.post)
        if form.is__valid():
            usuario= form.cleaned_data.get('username')
            contrasena= form.cleaned_data.get('password')
            user=authenticate(username=usuario, password=contrasena)
            if user is not None:
                login(request, user)
                messages.info(request, f"Bienvenido {usuario}")
                return redirect("INICIO.html")
            else:
                messages.error(request, "Usuario o contraseña incorrecta")
        else:
            messages.error(request, "Usuario o contraseña incorrecta")

    form= AuthenticationForm()
    return render(request, "login.html", {'form': form})
    
#MVC MODELO VISTA CONTROLADOR
#MVT MODELO TEMPLATE VISTA
