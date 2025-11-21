from django import forms
from django.forms import inlineformset_factory
from .models import (
    Receta, RecetaIngrediente, PasoPreparacion, Foto, Nutricional
)


# ==========================================================
#                  FORMULARIO DE RECETA
# ==========================================================
class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = [
            "categoria",
            "titulo",
            "descripcion",
            "porciones",
            "tiempo_preparacion",
            "tiempo_coccion",
            "dificultad",
        ]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }


# ==========================================================
#                FORMULARIO DE INGREDIENTES
# ==========================================================
class RecetaIngredienteForm(forms.ModelForm):
    class Meta:
        model = RecetaIngrediente
        fields = ["ingrediente", "cantidad", "unidad"]
        widgets = {
            "unidad": forms.TextInput(attrs={"placeholder": "g, ml, pieza..."})
        }


IngredientesFormSet = inlineformset_factory(
    Receta,
    RecetaIngrediente,
    form=RecetaIngredienteForm,
    extra=3,        # Número inicial de filas
    can_delete=True
)


# ==========================================================
#                FORMULARIO DE PASOS
# ==========================================================
class PasoPreparacionForm(forms.ModelForm):
    class Meta:
        model = PasoPreparacion
        fields = ["numero_paso", "descripcion", "tiempo_estimado"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 2}),
        }


PasosFormSet = inlineformset_factory(
    Receta,
    PasoPreparacion,
    form=PasoPreparacionForm,
    extra=3,
    can_delete=True
)


# ==========================================================
#                FORMULARIO DE FOTOS
# ==========================================================
class FotoForm(forms.ModelForm):
    class Meta:
        model = Foto
        fields = ["imagen", "descripcion", "es_principal"]


FotosFormSet = inlineformset_factory(
    Receta,
    Foto,
    form=FotoForm,
    extra=1,
    can_delete=True
)


# ==========================================================
#         FORMULARIO DE INFORMACIÓN NUTRICIONAL
# ==========================================================
class NutricionalForm(forms.ModelForm):
    class Meta:
        model = Nutricional
        fields = [
            "calorias",
            "carbohidratos",
            "proteinas",
            "grasas",
        ]


NutricionalFormSet = inlineformset_factory(
    Receta,
    Nutricional,
    form=NutricionalForm,
    extra=1,
    can_delete=False
)