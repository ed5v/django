import os
import sys
import django
import importlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

# Forzar recarga del módulo
from SIRENITA import views
importlib.reload(views)

from django.test import RequestFactory
from django.contrib.auth.models import User

# Crear una solicitud de prueba
factory = RequestFactory()
request = factory.get('/CUENTA/')

# Simular usuario admin
admin = User.objects.get(username='admin')
request.user = admin

print("=" * 60)
print("PROBANDO VISTA CUENTA CON USUARIO: admin")
print("="* 60)
print()

# Llamar a la vista recargada
response = views.CUENTA(request)

print()
print("=" * 60)
print(f"Respuesta HTTP: {response.status_code}")
print("=" * 60)
