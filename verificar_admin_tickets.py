import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

from SIRENITA.models import Pedido
from django.contrib.auth.models import User

# Obtener usuarios
admin = User.objects.get(username='admin')
nuevo = User.objects.get(username='nuevo')
pc = User.objects.get(username='pc')

print("=" * 60)
print("ANÁLISIS DE TICKETS PENDIENTES")
print("=" * 60)

# Verificar todos los tickets con items solicitados
base_qs = Pedido.objects.filter(
    estado_pago='PENDIENTE_DE_PAGO',
    items__solicitado=True
).distinct()

print(f"\n📊 TODOS los tickets pendientes con items solicitados:")
print(f"   Total: {base_qs.count()}")
for t in base_qs:
    print(f"   - Ticket #{t.id} → usuario: {t.usuario.username} (id={t.usuario.id})")

# Tickets que debería ver admin
admin_tickets = base_qs.filter(usuario=admin)
print(f"\n👤 Tickets que debería ver 'admin' (id={admin.id}):")
print(f"   Total: {admin_tickets.count()}")
for t in admin_tickets:
    print(f"   - Ticket #{t.id}")

# Tickets que debería ver nuevo
nuevo_tickets = base_qs.filter(usuario=nuevo)
print(f"\n👤 Tickets que debería ver 'nuevo' (id={nuevo.id}):")
print(f"   Total: {nuevo_tickets.count()}")
for t in nuevo_tickets:
    print(f"   - Ticket #{t.id}")

# Tickets que debería ver pc (todos)
print(f"\n🔧 Tickets que debería ver 'pc' (id={pc.id}) [TODOS]:")
print(f"   Total: {base_qs.count()}")
for t in base_qs:
    print(f"   - Ticket #{t.id}")

print("\n" + "=" * 60)
print("CONCLUSIÓN:")
print("=" * 60)
print(f"Si 'admin' ve el ticket #3, hay un problema con el filtro.")
print(f"El ticket #3 pertenece a '{nuevo.username}', no a '{admin.username}'.")
