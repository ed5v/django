"""
URL configuration for web_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from SIRENITA import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.INDEX, name="index"),
    path('INICIO/', views.INDEX, name= "INICIO"),
    path('AUDITORIA/', views.AUDITORIA, name= "AUDITORIA"),
    path('CAJA/', views.CAJA, name= "CAJA"),
    path('CUENTA/', views.CUENTA, name= "CUENTA"),
    path('INICIO/', views.INICIO, name= "INICIO"),
    path('INVENTARIO/', views.INVENTARIO, name= "INVENTARIO"),
    path('ORDEN/', views.ORDEN, name= "ORDEN"),
    
    #path('admin/', admin.site.urls),
    
    path('', include('SIRENITA.urls')),
    #path('save_article/', views.save_article, name= "save"),#
    #path('create_article/', views.create_article, name= "create")#
    
    #path('contacto/<str:nombre>', views.contacto, name= "contacto")#
    #path("hello/<name>", views.hello_there, name="hello_there")
    
]
