from django.db import models


# ===========================================
#                CATEGORÍAS
# ===========================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


# ===========================================
#                 PRODUCTOS
# ===========================================
class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name="productos")
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


# ===========================================
#                 PEDIDOS
# ===========================================
class Pedido(models.Model):
    numero_cliente = models.IntegerField()
    creado = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def __str__(self):
        return f"Pedido {self.numero_cliente}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    observaciones = models.TextField(blank=True)

    def subtotal(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


# ===========================================
#               RECETARIO (NUEVO)
# ===========================================
class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    unidad_base = models.CharField(max_length=20, blank=True, null=True)  # g, ml, pieza

    def __str__(self):
        return self.nombre


class Receta(models.Model):

    DIFICULTAD_CHOICES = [
        ('Fácil', 'Fácil'),
        ('Media', 'Media'),
        ('Difícil', 'Difícil'),
    ]

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        related_name="recetas"
    )

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    porciones = models.PositiveIntegerField(default=1)
    tiempo_preparacion = models.PositiveIntegerField(default=0, help_text="Minutos")
    tiempo_coccion = models.PositiveIntegerField(default=0, help_text="Minutos")
    dificultad = models.CharField(max_length=20, choices=DIFICULTAD_CHOICES, default="Fácil")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo


class RecetaIngrediente(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="ingredientes_detalle")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name="usos")
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    unidad = models.CharField(max_length=20)  # g, ml, cucharada, pieza...

    class Meta:
        unique_together = ('receta', 'ingrediente')

    def __str__(self):
        return f"{self.ingrediente.nombre} en {self.receta.titulo}"


class PasoPreparacion(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="pasos")
    numero_paso = models.PositiveIntegerField()
    descripcion = models.TextField()
    tiempo_estimado = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['numero_paso']

    def __str__(self):
        return f"Paso {self.numero_paso} - {self.receta.titulo}"


class Foto(models.Model):
    receta = models.ForeignKey(Receta, on_delete=models.CASCADE, related_name="fotos")
    imagen = models.ImageField(upload_to="recetas/")
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    es_principal = models.BooleanField(default=False)

    def __str__(self):
        return f"Foto de {self.receta.titulo}"


class Nutricional(models.Model):
    receta = models.OneToOneField(Receta, on_delete=models.CASCADE, related_name="nutricion")
    calorias = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    carbohidratos = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    proteinas = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    grasas = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Información nutricional de {self.receta.titulo}"