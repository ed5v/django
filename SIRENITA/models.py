from django.db import models
from django.contrib.auth.models import User


# ===========================================
#             CUPONES DE DESCUENTO
# ===========================================
class Cupon(models.Model):
    TIPO_DESCUENTO = [
        ('PORCENTAJE', 'Porcentaje'),
        ('FIJO', 'Monto Fijo'),
    ]
    
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True)
    tipo_descuento = models.CharField(max_length=15, choices=TIPO_DESCUENTO, default='PORCENTAJE')
    valor = models.DecimalField(max_digits=10, decimal_places=2, help_text="Porcentaje (0-100) o monto fijo")
    fecha_inicio = models.DateTimeField()
    fecha_expiracion = models.DateTimeField()
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ACTIVO')
    usos_maximos = models.PositiveIntegerField(default=0, help_text="0 = ilimitado")
    usos_actuales = models.PositiveIntegerField(default=0)
    creado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tbl_cupones'
        ordering = ['-creado']
    
    def __str__(self):
        return f"{self.codigo} - {self.tipo_descuento}: {self.valor}"
    
    def esta_vigente(self):
        """Verifica si el cupón está vigente por fecha"""
        from django.utils import timezone
        ahora = timezone.now()
        return self.fecha_inicio <= ahora <= self.fecha_expiracion
    
    def puede_usarse(self):
        """Verifica si el cupón está activo y vigente"""
        if self.estado != 'ACTIVO':
            return False, "Cupón inactivo"
        if not self.esta_vigente():
            return False, "Cupón expirado o aún no vigente"
        if self.usos_maximos > 0 and self.usos_actuales >= self.usos_maximos:
            return False, "Cupón agotado"
        return True, "Cupón válido"
    
    def calcular_descuento(self, monto_original):
        """Calcula el descuento aplicado sobre un monto"""
        if self.tipo_descuento == 'PORCENTAJE':
            return monto_original * (self.valor / 100)
        else:  # FIJO
            return min(self.valor, monto_original)  # No puede descontar más del total


# ===========================================
#                CATEGORÍAS
# ===========================================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


# ===========================================
#                   MESAS
# ===========================================
class Mesa(models.Model):
    mesa = models.IntegerField(unique=True)
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'SIRENITA_mesas'
        ordering = ['mesa']

    def __str__(self):
        return f"Mesa {self.mesa}"


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
    ESTADO_PAGO_CHOICES = [
        ('PENDIENTE_DE_PAGO', 'Pendiente de Pago'),
        ('PAGADO', 'Pagado'),
        ('CANCELADO', 'Cancelado'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('EFECTIVO', 'Efectivo'),
        ('TARJETA', 'Tarjeta'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('STRIPE', 'Stripe'),
        ('MERCADOPAGO', 'MercadoPago'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    numero_cliente = models.IntegerField(null=True, blank=True)
    mesa = models.IntegerField(null=True, blank=True)
    personas = models.IntegerField(null=True, blank=True)
    observaciones = models.TextField(null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    completado = models.BooleanField(default=False)
    
    # Campos de pago
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='PENDIENTE_DE_PAGO')
    cupon_aplicado = models.ForeignKey(Cupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fecha_pago = models.DateTimeField(null=True, blank=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, null=True, blank=True)

    def total(self):
        """Total sin descuento de items solicitados"""
        return sum(item.subtotal() for item in self.items.filter(solicitado=True))
    
    def total_con_descuento(self):
        """Total final con descuento aplicado"""
        return self.total() - self.descuento_aplicado

    def __str__(self):
        return f"Pedido {self.numero_cliente}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    observaciones = models.TextField(blank=True, null=True)
    solicitado = models.BooleanField(default=False)  # True cuando se envía a cocina/bar

    def subtotal(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"


# ===========================================
#        REGISTRO DE PEDIDOS SOLICITADOS
# ===========================================
class RegistroPedido(models.Model):
    """Tabla para registrar pedidos solicitados y gestionar pagos"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    observaciones = models.TextField(blank=True, null=True)
    pagado = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'tbl_registro_pedidos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Registro #{self.id} - Ticket #{self.ticket.id} - {self.producto.nombre}"


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


# ===========================================
#            AUDITORÍA DE ACCESOS
# ===========================================
class RegistroAcceso(models.Model):
    TIPO_ACCESO_CHOICES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('INTENTO_FALLIDO', 'Intento Fallido'),
    ]
    
    ESTADO_CHOICES = [
        ('EXITOSO', 'Exitoso'),
        ('FALLIDO', 'Fallido'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accesos')
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo_acceso = models.CharField(max_length=20, choices=TIPO_ACCESO_CHOICES)
    ip_address = models.GenericIPAddressField()
    navegador = models.CharField(max_length=255, blank=True, null=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES)
    observaciones = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'tbl_registro_accesos'
        ordering = ['-fecha_hora']
        verbose_name = 'Registro de Acceso'
        verbose_name_plural = 'Registros de Acceso'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.tipo_acceso} - {self.fecha_hora}"