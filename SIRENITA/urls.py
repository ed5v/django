from django.urls import path
from SIRENITA import views

urlpatterns = [
    path("", views.home, name="home"),
    
]