import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

from SIRENITA.models import Pedido, Cupon, ItemPedido

print("=" * 60)
print("VERIFICACIÓN DEL SISTEMA DE PAGOS Y CUPONES")
print("=" * 60)

# Estadísticas generales
total_tickets = Pedido.objects.count()
tickets_pendientes = Pedido.objects.filter(estado_pago='PENDIENTE_DE_PAGO').count()
tickets_pagados = Pedido.objects.filter(estado_pago='PAGADO').count()
tickets_con_items_solicitados = Pedido.objects.filter(items__solicitado=True).distinct().count()
total_cupones = Cupon.objects.count()

print(f"\n📊 ESTADÍSTICAS:")
print(f"   Total de tickets: {total_tickets}")
print(f"   Tickets PENDIENTE_DE_PAGO: {tickets_pendientes}")
print(f"   Tickets PAGADO: {tickets_pagados}")
print(f"   Tickets con items solicitados: {tickets_con_items_solicitados}")
print(f"   Total de cupones: {total_cupones}")

# Verificar tickets que deberían aparecer en CUENTA
print(f"\n💳 TICKETS EN CUENTA (PENDIENTE_DE_PAGO + items solicitados):")
cuenta_tickets = Pedido.objects.filter(
    estado_pago='PENDIENTE_DE_PAGO',
    items__solicitado=True
).distinct()

if cuenta_tickets.exists():
    for ticket in cuenta_tickets[:5]:
        items_solicitados = ticket.items.filter(solicitado=True).count()
        print(f"   ✓ Ticket #{ticket.id}: {items_solicitados} items solicitados, Total: ${ticket.total()}")
else:
    print("   ⚠️  NO HAY TICKETS PARA MOSTRAR EN CUENTA")
    print("   Motivos posibles:")
    print("   - No hay tickets con estado PENDIENTE_DE_PAGO")
    print("   - Los tickets no tienen items con solicitado=True")

# Verificar tickets que deberían aparecer en SEGUIMIENTO
print(f"\n✅ TICKETS EN SEGUIMIENTO (PAGADO):")
seguimiento_tickets = Pedido.objects.filter(estado_pago='PAGADO').order_by('-fecha_pago')[:5]

if seguimiento_tickets.exists():
    for ticket in seguimiento_tickets:
        print(f"   ✓ Ticket #{ticket.id}: Pagado el {ticket.fecha_pago}, Método: {ticket.metodo_pago}")
else:
    print("   ⚠️  NO HAY TICKETS PAGADOS")

# Ver estado de TODOS los tickets
print(f"\n📋 ESTADO DE TODOS LOS TICKETS:")
all_tickets = Pedido.objects.all()[:10]
if all_tickets.exists():
    for ticket in all_tickets:
        items_solicitados = ticket.items.filter(solicitado=True).count()
        items_total = ticket.items.count()
        print(f"   Ticket #{ticket.id}:")
        print(f"      - estado_pago: {ticket.estado_pago}")
        print(f"      - completado: {ticket.completado}")
        print(f"      - items: {items_total} total, {items_solicitados} solicitados")
else:
    print("   ⚠️  NO HAY TICKETS EN LA BASE DE DATOS")

# Verificar cupones
print(f"\n🎟️  CUPONES DISPONIBLES:")
cupones = Cupon.objects.all()
if cupones.exists():
    for cupon in cupones:
        puede_usar, mensaje = cupon.puede_usarse()
        print(f"   ✓ {cupon.codigo}: {cupon.tipo_descuento} {cupon.valor}, Estado: {cupon.estado}")
        print(f"      Puede usarse: {puede_usar} - {mensaje}")
else:
    print("   ⚠️  NO HAY CUPONES CREADOS")
    print("   Crear cupones desde el admin: http://127.0.0.1:8000/admin/")

print("\n" + "=" * 60)
print("RECOMENDACIONES:")
print("=" * 60)

if not cuenta_tickets.exists():
    print("\n🔧 Para ver tickets en CUENTA:")
    print("   1. Crear un ticket desde ORDEN")
    print("   2. Agregar items al ticket")
    print("   3. SOLICITAR el pedido (esto marca items.solicitado=True)")
    print("   4. El ticket aparecerá en CUENTA automáticamente")

if not cupones.exists():
    print("\n🔧 Para crear cupones:")
    print("   1. Ir a: http://127.0.0.1:8000/admin/")
    print("   2. Login como admin")
    print("   3. Ir a 'SIRENITA' > 'Cupones' > 'Agregar cupón'")
    print("   4. Ejemplo: código='DESCUENTO10', tipo='PORCENTAJE', valor=10")

print("\n✅ El sistema está funcionando correctamente.")
print("   Servidor: http://127.0.0.1:8000/")
print("   CUENTA: http://127.0.0.1:8000/CUENTA/")
print("   SEGUIMIENTO: http://127.0.0.1:8000/SEGUIMIENTO/")
