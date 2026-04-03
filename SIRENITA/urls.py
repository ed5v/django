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
    path('', views.INDEX, name='index'),                      # Página principal
    path('login/', views.login_request, name="login"),        # URL explícita
    path('logout/', views.logout_request, name="logout"),     # Cerrar sesión

    # --- PÁGINAS PRINCIPALES ---
    path('INDEX/', views.INDEX, name='INDEX'),
    path('INICIO/', views.INICIO, name='INICIO'),
    path('CUENTA/', views.CUENTA, name='CUENTA'),
    path('SEGUIMIENTO/', views.SEGUIMIENTO, name='SEGUIMIENTO'),

    # --- ORDENES ---
    path('ORDEN/', views.ORDEN, name='ORDEN'),
    path('crear_ticket/', views.crear_ticket, name='crear_ticket'),
    path('actualizar_datos_ticket/', views.actualizar_datos_ticket, name='actualizar_datos_ticket'),
    path('cancelar_ticket/', views.cancelar_ticket, name='cancelar_ticket'),
    path('agregar_item/', views.agregar_item, name='agregar_item'),
    path('editar_item_ticket/', views.editar_item_ticket, name='editar_item_ticket'),
    path('eliminar_item_ticket/', views.eliminar_item_ticket, name='eliminar_item_ticket'),
    path('solicitar_pedido/', views.solicitar_pedido, name='solicitar_pedido'),
    path('registros_pedidos/', views.listar_registros_pedidos, name='listar_registros_pedidos'),
    path('marcar_pagado/<int:registro_id>/', views.marcar_pagado, name='marcar_pagado'),
    path('accion/<int:numero>/', views.agregar_orden, name='accion'),
    path('api/ticket/<int:numero_cliente>/', views.obtener_ticket, name='obtener_ticket'),

    #path('REGISTRO/', views.listar_registros_pedidos, name='REGISTRO'),
    #path('registro_pedidos/', views.listar_registros_pedidos, name='Registro_pedidos'),

    # --- MÓDULOS PROTEGIDOS ---
    path('INVENTARIO/', views.INVENTARIO, name='INVENTARIO'),
    path('CAJA/', views.CAJA, name='CAJA'),
    path('AUDITORIA/', views.AUDITORIA, name='AUDITORIA'),
    
    # --- RECETAS ---
    path('recetas/', views.lista_recetas, name='lista_recetas'),
    path('recetas/<int:pk>/', views.detalle_receta, name='detalle_receta'),
    path('recetas/crear/', views.crear_receta, name='crear_receta'),
    path('recetas/<int:pk>/editar/', views.editar_receta, name='editar_receta'),
    path('recetas/<int:pk>/eliminar/', views.eliminar_receta, name='eliminar_receta'),
    
    # --- GESTIÓN DE PAGOS Y CUPONES ---
    path('validar_cupon/', views.validar_cupon, name='validar_cupon'),
    path('aplicar_cupon/', views.aplicar_cupon, name='aplicar_cupon'),
    path('remover_cupon/', views.remover_cupon, name='remover_cupon'),
    path('pagar_ticket/', views.pagar_ticket, name='pagar_ticket'),
    path('pagar_item_individual/', views.pagar_item_individual, name='pagar_item_individual'),
]
