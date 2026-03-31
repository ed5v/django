import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from SIRENITA.views import CUENTA

# Crear una solicitud de prueba
factory = RequestFactory()
request = factory.get('/CUENTA/')

# Simular usuario admin
admin = User.objects.get(username='admin')
request.user = admin

print("=" * 60)
print("SIMULANDO VISTA CUENTA CON USUARIO: admin")
print("=" * 60)

# Llamar a la vista
response = CUENTA(request)

print(f"\nRespuesta recibida: {response.status_code}")
print("\n" + "=" * 60)
