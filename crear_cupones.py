import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

from django.utils import timezone
from SIRENITA.models import Cupon

print("Creando cupones de ejemplo...")

# Cupón de porcentaje
cupon1, created1 = Cupon.objects.get_or_create(
    codigo='DESCUENTO10',
    defaults={
        'tipo_descuento': 'PORCENTAJE',
        'valor': 10,
        'fecha_inicio': timezone.now(),
        'fecha_expiracion': timezone.now() + timedelta(days=30),
        'estado': 'ACTIVO',
        'usos_maximos': 100,
    }
)
if created1:
    print(f"✓ Creado: {cupon1.codigo} - 10% de descuento")
else:
    print(f"✓ Ya existe: {cupon1.codigo}")

# Cupón de monto fijo
cupon2, created2 = Cupon.objects.get_or_create(
    codigo='PROMO50',
    defaults={
        'tipo_descuento': 'FIJO',
        'valor': 50,
        'fecha_inicio': timezone.now(),
        'fecha_expiracion': timezone.now() + timedelta(days=30),
        'estado': 'ACTIVO',
        'usos_maximos': 50,
    }
)
if created2:
    print(f"✓ Creado: {cupon2.codigo} - $50 de descuento fijo")
else:
    print(f"✓ Ya existe: {cupon2.codigo}")

# Cupón VIP
cupon3, created3 = Cupon.objects.get_or_create(
    codigo='VIP20',
    defaults={
        'tipo_descuento': 'PORCENTAJE',
        'valor': 20,
        'fecha_inicio': timezone.now(),
        'fecha_expiracion': timezone.now() + timedelta(days=90),
        'estado': 'ACTIVO',
        'usos_maximos': 0,  # Ilimitado
    }
)
if created3:
    print(f"✓ Creado: {cupon3.codigo} - 20% descuento VIP (ilimitado)")
else:
    print(f"✓ Ya existe: {cupon3.codigo}")

print("\n" + "="*60)
print("CUPONES DISPONIBLES PARA USAR:")
print("="*60)
for cupon in Cupon.objects.filter(estado='ACTIVO'):
    puede_usar, mensaje = cupon.puede_usarse()
    print(f"\n{cupon.codigo}:")
    print(f"  Tipo: {cupon.get_tipo_descuento_display()}")
    print(f"  Valor: {cupon.valor}")
    print(f"  Válido: {mensaje}")
    print(f"  Usos: {cupon.usos_actuales}/{cupon.usos_maximos if cupon.usos_maximos > 0 else '∞'}")
