from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

# Importación del modelo CustomUser
from .models.user import CustomUser

class CustomUserCreationForm(AdminUserCreationForm):
    email = forms.EmailField(
        label=_("Correo Electrónico"),
        max_length=254,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text=_("Ingrese un correo electrónico válido.")
    )
    
    phone_number = forms.CharField(
        label=_("Número de Teléfono"),
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text=_("Formato: +999999999")
    )
    
    birth_date = forms.DateField(
        label=_("Fecha de Nacimiento"),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text=_("Formato: AAAA-MM-DD")
    )
    
    gender = forms.ChoiceField(
        label=_("Género"),
        choices=CustomUser.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = (
            'username', 
            'email', 
            'password1', 
            'password2', 
            'phone_number', 
            'birth_date', 
            'gender'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        """
        Validación personalizada para el correo electrónico
        """
        email = self.cleaned_data.get('email')
        
        # Validar que el email no exista previamente
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError(_("Ya existe un usuario con este correo electrónico."))
        
        return email

    def clean_birth_date(self):
        """
        Validación de fecha de nacimiento
        """
        birth_date = self.cleaned_data.get('birth_date')
        
        if birth_date:
            # Ejemplo de validación de edad mínima
            from datetime import date
            today = date.today()
            age = today.year - birth_date.year - (
                (today.month, today.day) < (birth_date.month, birth_date.day)
            )
            
            if age < 13:
                raise ValidationError(_("Debes tener al menos 13 años para registrarte."))
        
        return birth_date

    def save(self, commit=True):
        """
        Método personalizado de guardado
        """
        user = super().save(commit=False)
        
        # Configuraciones adicionales al guardar
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
        
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Formulario para actualización de datos de usuario
    """
    class Meta:
        model = CustomUser
        fields = (
            'username', 
            'email', 
            'phone_number', 
            'birth_date', 
            'gender'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'})
        }

    def clean_email(self):
        """
        Validación de email único al actualizar
        """
        email = self.cleaned_data.get('email')
        
        # Excluir el usuario actual de la validación
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("Ya existe un usuario con este correo electrónico."))
        
        return email


class UserProfileUpdateForm(forms.ModelForm):
    """
    Formulario específico para actualización de perfil
    """
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'phone_number', 
            'birth_date', 
            'gender'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'})
        }

    def clean_email(self):
        """
        Validación de email único
        """
        email = self.cleaned_data.get('email')
        
        # Excluir el usuario actual de la validación
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError(_("Ya existe un usuario con este correo electrónico."))
        
        return email