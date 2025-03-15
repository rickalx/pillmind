from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

#from .user import CustomUser  

class Especialidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class NivelAcceso(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class Rol(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre

class PerfilProfesional(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='perfil_profesional'
    )
    
    # Múltiples especialidades
    especialidades = models.ManyToManyField(
        Especialidad, 
        blank=True
    )
    
    # Nivel de acceso
    nivel_acceso = models.ForeignKey(
        NivelAcceso, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Información profesional
    titulo_profesional = models.CharField(max_length=100, blank=True)
    institucion = models.CharField(max_length=100, blank=True)
    años_experiencia = models.IntegerField(default=0)
    
    # Roles específicos
    roles = models.ManyToManyField(
        Rol, 
        blank=True
    )
    
    # Información adicional
    biografia = models.TextField(blank=True)
    certificaciones = models.TextField(blank=True)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"