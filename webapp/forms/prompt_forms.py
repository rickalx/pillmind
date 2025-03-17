from django import forms
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from ..models.prompt import Prompt, RolIA
import json

class PromptForm(forms.ModelForm):
    """
    Formulario para crear y editar prompts
    """
    # Campo para texto simple de etiquetas separadas por comas
    etiquetas_texto = forms.CharField(
        label=_("Etiquetas"),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ej: medicina, nutrición, pediatría'}),
        help_text=_("Ingrese las etiquetas separadas por comas")
    )
    
    class Meta:
        model = Prompt
        fields = [
            'objetivo',
            'rol_ia',
            'texto',
            'version',
            'especialidades',
            'estado',
            # Quitamos 'etiquetas' de los campos del modelo y usamos nuestro campo personalizado
        ]
        exclude = ['etiquetas']
        widgets = {
            'objetivo': forms.TextInput(attrs={'class': 'form-control'}),
            'rol_ia': forms.Select(attrs={'class': 'form-control'}),
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 8}),
            'version': forms.TextInput(attrs={'class': 'form-control'}),
            'especialidades': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'objetivo': _('Propósito principal del prompt'),
            'rol_ia': _('Rol que debe asumir la IA al utilizar este prompt'),
            'texto': _('Contenido completo del prompt'),
            'version': _('Versión del prompt (ej: 1.0.0)'),
            'especialidades': _('Especialidades relacionadas con este prompt'),
            'estado': _('Estado actual del prompt'),
        }

    def clean_etiquetas_texto(self):
        """Convierte el texto de etiquetas separado por comas a una lista."""
        etiquetas_texto = self.cleaned_data.get('etiquetas_texto', '')
        if not etiquetas_texto:
            return []
            
        # Convertir string separado por comas a lista
        etiquetas_lista = [tag.strip() for tag in etiquetas_texto.split(',') if tag.strip()]
        return etiquetas_lista

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        
        # Si hay una instancia existente, preparamos los datos iniciales
        if instance and instance.etiquetas:
            # Convertir la lista de etiquetas a texto separado por comas
            if isinstance(instance.etiquetas, list):
                etiquetas_texto = ", ".join(instance.etiquetas)
            elif isinstance(instance.etiquetas, str):
                try:
                    # Intenta analizar las etiquetas si están en formato JSON
                    etiquetas_lista = json.loads(instance.etiquetas)
                    if isinstance(etiquetas_lista, list):
                        etiquetas_texto = ", ".join(etiquetas_lista)
                    else:
                        etiquetas_texto = instance.etiquetas
                except json.JSONDecodeError:
                    etiquetas_texto = instance.etiquetas
            else:
                etiquetas_texto = ""
            
            # Si no hay initial data, la creamos
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            
            # Establecemos el valor inicial para etiquetas_texto
            kwargs['initial']['etiquetas_texto'] = etiquetas_texto
            
        super().__init__(*args, **kwargs)
        
        # Resto de tu inicialización...

    def save(self, commit=True):
        """
        Guarda el formulario y maneja la conversión de etiquetas
        """
        instance = super().save(commit=False)
        
        # Asignar la lista de etiquetas al campo del modelo
        instance.etiquetas = self.cleaned_data.get('etiquetas_texto', [])
        
        if commit:
            # Guardamos directamente para evitar problemas con el historial
            # en la primera creación
            instance.save(update_historial=False)  # Parámetro especial para evitar actualizar historial
            self.save_m2m()  # Para guardar las relaciones many-to-many
            
        return instance
