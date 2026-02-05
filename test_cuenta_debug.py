import os
import sys
import django
from io import StringIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from SIRENITA.views import CUENTA

# Capturar stdout
old_stdout = sys.stdout
sys.stdout = captured_output = StringIO()

# Crear una solicitud de prueba
factory = RequestFactory()
request = factory.get('/CUENTA/')

# Simular usuario admin
admin = User.objects.get(username='admin')
request.user = admin

print("=" * 60)
print("SIMULANDO VISTA CUENTA CON USUARIO: admin")
print("=" * 60)

# Llamar a la vista (esto debería generar los prints de debug)
response = CUENTA(request)

# Restaurar stdout
sys.stdout = old_stdout

# Mostrar lo capturado
output = captured_output.getvalue()
print(output)

if "[DEBUG CUENTA]" in output:
    print("\n✅ Logs de debug encontrados en el output")
else:
    print("\n❌ NO se encontraron logs de debug - posible problema de caché")
