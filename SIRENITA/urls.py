from django.urls import path
from SIRENITA import views

urlpatterns = [
    #path('', views.home, name="home"),
    
    path('', views.ORDEN, name='tabla'),
    path('accion/<int:numero>/',views.agregar_orden, name='accion'),
]
