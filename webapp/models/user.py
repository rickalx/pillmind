from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date
from .soft_delete import SoftDeleteModel

class CustomUser(AbstractUser, SoftDeleteModel):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro')
    ]

    # Validadores
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', 
        message="Número de teléfono debe estar en formato: '+999999999'"
    )

    # Campos extendidos
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True
    )
    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES, 
        blank=True
    )
    birth_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Métodos de gestión de usuarios
    @classmethod
    def create_user(cls, username, email, password=None, **extra_fields):
        """
        Método de clase para crear un nuevo usuario
        """
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        
        # Normalizar email
        email = cls.normalize_email(email)
        
        # Crear usuario
        user = cls(username=username, email=email, **extra_fields)
        
        # Establecer contraseña
        if password:
            user.set_password(password)
        
        user.save()
        return user

    @classmethod
    def create_superuser(cls, username, email, password=None, **extra_fields):
        """
        Método de clase para crear un superusuario
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuario debe tener is_staff=True')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuario debe tener is_superuser=True')
        
        return cls.create_user(username, email, password, **extra_fields)

    def deactivate_account(self):
        """
        Método para desactivar cuenta de usuario
        """
        self.is_active = False
        self.save()

    def reactivate_account(self):
        """
        Método para reactivar cuenta de usuario
        """
        self.is_active = True
        self.save()

    def update_profile(self, **kwargs):
        """
        Método para actualizar información de perfil
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        self.save()

    def validate_unique_email(self):
        """
        Validación personalizada para email único
        """
        if CustomUser.objects.filter(email=self.email).exclude(pk=self.pk).exists():
            raise ValidationError({
                'email': _("Ya existe un usuario con este correo electrónico.")
            })

    def clean(self):
        """
        Método de validación personalizado
        """
        super().clean()
        self.validate_unique_email()
        
        # Validaciones adicionales
        if self.birth_date and self.birth_date > timezone.now().date():
            raise ValidationError({
                'birth_date': _("La fecha de nacimiento no puede ser futura.")
            })

    def save(self, *args, **kwargs):
        """
        Sobrescribir método save para validaciones
        """
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        """
        Representación en cadena del usuario
        """
        return f"{self.username} ({self.email})"

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
