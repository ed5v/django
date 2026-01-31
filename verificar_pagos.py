import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'web_project.settings')
django.setup()

from SIRENITA.models import Pedido, ItemPedido, RegistroPedido

print("=" * 70)
print("VERIFICACIÓN DEL SISTEMA DE PAGOS - INDIVIDUAL Y TOTAL")
print("=" * 70)

# Estadísticas
tickets_pendientes = Pedido.objects.filter(estado_pago='PENDIENTE_DE_PAGO', items__solicitado=True).distinct()
tickets_pagados = Pedido.objects.filter(estado_pago='PAGADO')

print(f"\n📊 RESUMEN:")
print(f"   Tickets pendientes de pago: {tickets_pendientes.count()}")
print(f"   Tickets completamente pagados: {tickets_pagados.count()}")

print(f"\n💳 TICKETS DISPONIBLES EN CUENTA:")
if tickets_pendientes.exists():
    for ticket in tickets_pendientes:
        items_solicitados = ticket.items.filter(solicitado=True)
        items_pagados = RegistroPedido.objects.filter(ticket=ticket, pagado=True).count()
        
        print(f"\n   📝 Ticket #{ticket.id}")
        print(f"      Estado: {ticket.estado_pago}")
        print(f"      Total original: ${ticket.total()}")
        if ticket.cupon_aplicado:
            print(f"      Cupón aplicado: {ticket.cupon_aplicado.codigo} (-${ticket.descuento_aplicado})")
            print(f"      Total con descuento: ${ticket.total_con_descuento()}")
        
        print(f"\n      📦 ARTÍCULOS ({items_solicitados.count()} items):")
        for item in items_solicitados:
            # Verificar si este item específico ya fue pagado
            pagado = RegistroPedido.objects.filter(
                ticket=ticket,
                producto=item.producto,
                cantidad=item.cantidad,
                pagado=True
            ).exists()
            
            estado = "✅ PAGADO" if pagado else "⏳ PENDIENTE"
            print(f"         - {item.cantidad}x {item.producto.nombre} (${item.subtotal()}) {estado}")
        
        print(f"\n      💰 Items pagados: {items_pagados}/{items_solicitados.count()}")
        print(f"      ⚡ Opciones disponibles:")
        print(f"         1. Pagar item individual (botón en cada artículo)")
        print(f"         2. Pagar ticket completo (botón principal)")
else:
    print("   ⚠️  NO HAY TICKETS PENDIENTES")

print(f"\n✅ TICKETS PAGADOS (Visibles en SEGUIMIENTO):")
if tickets_pagados.exists():
    for ticket in tickets_pagados:
        print(f"   Ticket #{ticket.id}: Pagado el {ticket.fecha_pago}, Método: {ticket.metodo_pago}")
        print(f"      Total pagado: ${ticket.total_con_descuento()}")
else:
    print("   Ningún ticket pagado aún")

print("\n" + "=" * 70)
print("FUNCIONALIDADES DISPONIBLES:")
print("=" * 70)
print("""
1. 💳 PAGO TOTAL DEL TICKET:
   - Paga todos los items solicitados de una vez
   - Aplica descuento de cupón si hay uno activo
   - Ticket se mueve a SEGUIMIENTO inmediatamente
   - Se crean registros de pago para todos los items

2. 💰 PAGO INDIVIDUAL DE ITEMS:
   - Cada artículo tiene su botón "💳 Pagar Item"
   - Se paga solo ese item específico
   - Item se marca visualmente como pagado
   - Si todos los items se pagan individualmente, el ticket completo se marca como PAGADO

3. 🎟️ CUPONES DE DESCUENTO:
   - Se pueden aplicar cupones antes del pago
   - Descuento se calcula automáticamente
   - Uso del cupón se registra
   - Cupones disponibles: DESCUENTO10, PROMO50, VIP20

4. 📊 REGISTRO DE PAGOS:
   - Cada pago (total o individual) se registra en la base de datos
   - Se mantiene historial completo de transacciones
   - Visible en tabla RegistroPedido
""")

print("🌐 URLs:")
print("   CUENTA: http://127.0.0.1:8000/CUENTA/")
print("   SEGUIMIENTO: http://127.0.0.1:8000/SEGUIMIENTO/")
print("   Admin: http://127.0.0.1:8000/admin/")
