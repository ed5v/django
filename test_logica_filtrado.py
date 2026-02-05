import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

from SIRENITA.models import Pedido
from django.contrib.auth.models import User

# Obtener usuario admin
admin = User.objects.get(username='admin')

print("=" * 60)
print(f"SIMULANDO LÓGICA DE CUENTA PARA: {admin.username} (id={admin.id})")
print("=" * 60)

# Base queryset (IGUAL QUE EN LA VISTA)
base_qs = Pedido.objects.filter(
    estado_pago='PENDIENTE_DE_PAGO',
    items__solicitado=True
)

print(f"\n1️⃣ Base queryset (sin filtro de usuario): {base_qs.distinct().count()} tickets")

# Aplicar lógica de filtrado (IGUAL QUE EN LA VISTA)
if admin.username == 'pc':
    tickets_qs = base_qs
    print(f"2️⃣ Usuario es 'pc' → Mostrando TODOS los tickets")
else:
    tickets_qs = base_qs.filter(usuario=admin)
    print(f"2️⃣ Usuario NO es 'pc' → Filtrando por usuario={admin.username}")

tickets_qs = tickets_qs.distinct()

print(f"3️⃣ Tickets después del filtro: {tickets_qs.count()}")
print(f"\n📋 Lista de tickets que debería ver '{admin.username}':")
for t in tickets_qs:
    print(f"   - Ticket #{t.id} (usuario: {t.usuario.username})")

print("\n" + "=" * 60)
if tickets_qs.filter(id=3).exists():
    print("❌ PROBLEMA: El ticket #3 APARECE en los resultados")
    print(f"   El ticket #3 pertenece a: {Pedido.objects.get(id=3).usuario.username}")
    print(f"   Pero está siendo mostrado al usuario: {admin.username}")
else:
    print("✅ CORRECTO: El ticket #3 NO aparece en los resultados")
