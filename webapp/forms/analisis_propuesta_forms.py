from django import forms
from ..models.analisis_propuesta import AnalisisPropuesta

class AnalisisPropuestaForm(forms.ModelForm):
    class Meta:
        model = AnalisisPropuesta
        fields = [
            'url_propuesta', 
            'contenido', 
            'prompts_utilizados', 
            'estado', 
            'palabras_clave'
        ]
        widgets = {
            'url_propuesta': forms.URLInput(attrs={'class': 'form-control'}),
            'contenido': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'prompts_utilizados': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'palabras_clave': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean_url_propuesta(self):
        url = self.cleaned_data.get('url_propuesta')
        # Validaciones adicionales de URL si es necesario
        return url