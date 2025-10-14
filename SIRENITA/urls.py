from django.urls import path
from SIRENITA import views

urlpatterns = [
    #path('', views.home, name="home"),
    
    path('', views.ORDEN, name='tabla'),
    path('accion/<int:numero>/',views.agregar_orden, name='accion'),
    #path('registro/', views.registro, name="registro"),
    path('logout/', views.logout_request, name="logout"),
    path('api/ticket/<int:numero_cliente>/', views.obtener_ticket, name='obtener_ticket'),
    path('login/', views.login_request, name="login"),
]
