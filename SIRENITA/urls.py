from django.urls import path
from . import views


'''urlpatterns = [
    #path('', views.login_request, name="home"),
    
    path('', views.ORDEN, name='tabla'),
    path('accion/<int:numero>/',views.agregar_orden, name='accion'),
    #path('registro/', views.registro, name="registro"),
    path('logout/', views.logout_request, name="logout"),
    path('api/ticket/<int:numero_cliente>/', views.obtener_ticket, name='obtener_ticket'),
    path('login/', views.login_request, name="login"),
]
'''

urlpatterns = [
    # --- AUTENTICACIÓN ---
    #path('', views.login_request, name="login"),             # Página principal → login
    path('login/', views.login_request, name="login"),        # URL explícita
    path('logout/', views.logout_request, name="logout"),     # Cerrar sesión

    # --- ORDENES ---
    path('ORDEN/', views.ORDEN, name='ORDEN'),
    path('crear_ticket/', views.crear_ticket, name='crear_ticket'),
    path('agregar_item/', views.agregar_item, name='agregar_item'),
    path('accion/<int:numero>/', views.agregar_orden, name='accion'),
    path('api/ticket/<int:numero_cliente>/', views.obtener_ticket, name='obtener_ticket'),

    # --- MÓDULOS PROTEGIDOS ---
    path('INVENTARIO/', views.INVENTARIO, name='INVENTARIO'),
    path('CAJA/', views.CAJA, name='CAJA'),
    path('AUDITORIA/', views.AUDITORIA, name='AUDITORIA'),
]
