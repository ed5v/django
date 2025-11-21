from django.contrib import admin
from .models import (
    Categoria, Producto, Pedido, ItemPedido,
    Ingrediente, Receta, RecetaIngrediente,
    PasoPreparacion, Foto, Nutricional
)

# =====================================================
#                PRODUCTOS - ADMIN
# =====================================================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio", "disponible")
    list_filter = ("categoria", "disponible")
    search_fields = ("nombre",)
    list_editable = ("precio", "disponible")


# =====================================================
#                 PEDIDOS - ADMIN
# =====================================================
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1
    autocomplete_fields = ("producto",)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "numero_cliente", "creado", "completado", "total_mostrar")
    list_filter = ("completado", "creado")
    search_fields = ("numero_cliente",)
    inlines = [ItemPedidoInline]

    def total_mostrar(self, obj):
        return f"${obj.total():.2f}"
    total_mostrar.short_description = "Total"


# =====================================================
#               RECETARIO - ADMIN
# =====================================================
class RecetaIngredienteInline(admin.TabularInline):
    model = RecetaIngrediente
    extra = 1
    autocomplete_fields = ("ingrediente",)


class PasoPreparacionInline(admin.TabularInline):
    model = PasoPreparacion
    extra = 1


class FotoInline(admin.TabularInline):
    model = Foto
    extra = 1


class NutricionalInline(admin.StackedInline):
    model = Nutricional
    extra = 0


@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "unidad_base")
    search_fields = ("nombre",)


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "porciones", "dificultad", "fecha_creacion")
    list_filter = ("categoria", "dificultad")
    search_fields = ("titulo",)
    inlines = [
        RecetaIngredienteInline,
        PasoPreparacionInline,
        FotoInline,
        NutricionalInline
    ]


# Registrar modelos simples
admin.site.register(RecetaIngrediente)
admin.site.register(PasoPreparacion)
admin.site.register(Foto)
admin.site.register(Nutricional)