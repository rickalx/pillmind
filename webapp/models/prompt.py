from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import uuid
from .models import Especialidad
from .soft_delete import SoftDeleteModel

class RolIA(models.Model):
    """
    Modelo para representar roles que puede asumir la IA en los prompts
    """
    nombre = models.CharField(
        max_length=100, 
        verbose_name=_('Nombre'),
        help_text=_('Nombre del rol que puede asumir la IA')
    )
    
    descripcion = models.TextField(
        blank=True, 
        verbose_name=_('Descripción'),
        help_text=_('Descripción detallada del rol de IA')
    )
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = _('Rol de IA')
        verbose_name_plural = _('Roles de IA')
        ordering = ['nombre']

class HistorialModificacion(SoftDeleteModel):
    """
    Modelo para rastrear modificaciones de prompts
    """
    prompt = models.ForeignKey(
        'Prompt', 
        on_delete=models.CASCADE, 
        related_name='historial_modificaciones',
        verbose_name=_('Prompt')
    )
    version = models.CharField(max_length=20, verbose_name=_('Versión'))
    texto_anterior = models.TextField(verbose_name=_('Texto Anterior'))
    fecha_modificacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Modificación'))
    
    def __str__(self):
        return f"Modificación {self.version} - {self.fecha_modificacion}"

    class Meta:
        verbose_name = _('Historial de Modificación')
        verbose_name_plural = _('Historiales de Modificación')
        ordering = ['-fecha_modificacion']

class Prompt(SoftDeleteModel):
    """
    Modelo principal de Prompt
    """
    # Identificador único
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )

    # Información básica
    objetivo = models.CharField(
        max_length=255, 
        verbose_name=_('Objetivo del Prompt')
    )

    # Relación con RolIA (SET_NULL para no perder el prompt si se elimina el rol)
    rol_ia = models.ForeignKey(
        RolIA, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='prompts_con_este_rol',
        verbose_name=_('Rol de IA Asignado'),
        help_text=_('Rol que debe asumir la IA al utilizar este prompt')
    )

    # Texto del prompt
    texto = models.TextField(
        verbose_name=_('Texto del Prompt')
    )
    
    # Formato de respuesta esperado
    formato_respuesta = models.TextField(
        verbose_name=_('Formato de Respuesta'),
        blank=True,
        help_text=_('Estructura o formato que debe seguir la respuesta del modelo de IA')
    )

    # Información de versión
    version = models.CharField(
        max_length=20, 
        default='1.0.0',
        verbose_name=_('Versión')
    )

    # Especialidades relacionadas
    especialidades = models.ManyToManyField(
        Especialidad, 
        blank=True,
        verbose_name=_('Especialidades')
    )

    # Información del autor (con protección contra eliminación)
    class AutorInfo(SoftDeleteModel):
        username = models.CharField(max_length=150)
        email = models.EmailField(max_length=254, blank=True)
        first_name = models.CharField(max_length=150, blank=True)
        last_name = models.CharField(max_length=150, blank=True)

        def __str__(self):
            return self.username

    # Relación con usuario
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='prompts_creados',
        verbose_name=_('Autor')
    )

    # Información de autor desnormalizada
    # Cambiado de OneToOneField a ForeignKey
    autor_info = models.ForeignKey(
        AutorInfo, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_('Información de Autor')
    )

    # Fechas
    fecha_creacion = models.DateTimeField(
        default=timezone.now, 
        verbose_name=_('Fecha de Creación')
    )
    fecha_ultima_modificacion = models.DateTimeField(
        auto_now=True, 
        verbose_name=_('Fecha de Última Modificación')
    )

    # Estado del prompt
    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR', _('Borrador')
        PUBLICADO = 'PUBLICADO', _('Publicado')
        REVISADO = 'REVISADO', _('Revisado')
        EN_REVISION = 'EN_REVISION', _('En Revisión')
        RECHAZADO = 'RECHAZADO', _('Rechazado')
    
    estado = models.CharField(
        max_length=20, 
        choices=Estado.choices, 
        default=Estado.BORRADOR,
        verbose_name=_('Estado')
    )
    
    # Nuevo campo para indicar si es el prompt predeterminado para el chatbot
    es_predeterminado = models.BooleanField(
        default=False, 
        verbose_name=_('Es predeterminado para chatbot'),
        help_text=_('Si está marcado, este prompt se utilizará por defecto en el chatbot')
    )
    
    # Método para cambiar estado
    def cambiar_estado(self, nuevo_estado):
        """
        Cambiar el estado del prompt
        """
        if nuevo_estado in dict(self.Estado.choices):
            self.estado = nuevo_estado
            self.save()
        else:
            raise ValueError(_("Estado no válido"))
    
    # Etiquetas
    etiquetas = models.JSONField(
        verbose_name=_('Etiquetas'),
        default=list,
        blank=True,
        help_text=_('Lista de etiquetas asociadas al prompt')
    )

    def save(self, *args, update_historial=True, **kwargs):
        """
        Sobrescribir método save para gestionar historial y autor
        """
        if self.es_predeterminado:
            # Desactivar cualquier otro prompt predeterminado
            Prompt.objects.filter(es_predeterminado=True).exclude(pk=self.pk).update(es_predeterminado=False)
        
        # Crear o actualizar información de autor
        if self.autor:
            autor_info, created = self.AutorInfo.objects.get_or_create(
                username=self.autor.username,
                defaults={
                    'email': self.autor.email,
                    'first_name': self.autor.first_name,
                    'last_name': self.autor.last_name
                }
            )
            
            # Si no es creación, actualizar información
            if not created:
                autor_info.email = self.autor.email
                autor_info.first_name = self.autor.first_name
                autor_info.last_name = self.autor.last_name
                autor_info.save()
            
            self.autor_info = autor_info

        # Verificar si es una modificación y si debemos actualizar el historial
        if update_historial and self.pk:
            try:
                prompt_original = Prompt.objects.get(pk=self.pk)
                if prompt_original.texto != self.texto:
                    # Crear registro en historial de modificaciones
                    HistorialModificacion.objects.create(
                        prompt=self,
                        version=self.version,
                        texto_anterior=prompt_original.texto
                    )
            except Prompt.DoesNotExist:
                pass  # No hacemos nada si es un nuevo objeto

        # Eliminar update_historial de kwargs para no pasarlo a super().save()
        if 'update_historial' in kwargs:
            del kwargs['update_historial']
            
        super().save(*args, **kwargs)

    def get_autor_display(self):
        """
        Obtener nombre del autor
        """
        if self.autor_info:
            # Priorizar nombre completo
            if self.autor_info.first_name and self.autor_info.last_name:
                return f"{self.autor_info.first_name} {self.autor_info.last_name}"
            # Sino, usar username
            return self.autor_info.username
        return _('Autor Eliminado')

    def get_autor_email(self):
        """
        Obtener email del autor
        """
        return self.autor_info.email if self.autor_info else _('Email no disponible')

    def __str__(self):
        return f"{self.objetivo} (v{self.version})"

    class Meta:
        verbose_name = _('Prompt')
        verbose_name_plural = _('Prompts')
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['objetivo']),
            models.Index(fields=['autor', 'fecha_creacion']),
            models.Index(fields=['version'])
        ]
