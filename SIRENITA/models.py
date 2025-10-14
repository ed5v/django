from django.db import models

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    numero_cliente = models.IntegerField()
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - Cliente {self.numero_cliente}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    observaciones = models.TextField(blank=True, null=True)
    cantidad = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.nombre} (Pedido #{self.pedido.id})"