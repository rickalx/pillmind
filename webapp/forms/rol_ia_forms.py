from django import forms
from django.utils.translation import gettext_lazy as _

from ..models.prompt import RolIA

class RolIAForm(forms.ModelForm):
    """
    Formulario para el modelo RolIA
    """
    class Meta:
        model = RolIA
        fields = ['nombre', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
