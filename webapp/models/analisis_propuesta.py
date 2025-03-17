from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from .soft_delete import SoftDeleteModel

class AnalisisPropuesta(SoftDeleteModel):
    # Definición de estados
    class Estado(models.TextChoices):
        BORRADOR = 'BORRADOR', _('Borrador')
        PUBLICADO = 'PUBLICADO', _('Publicado')
        REVISADO = 'REVISADO', _('Revisado')
        EN_REVISION = 'EN_REVISION', _('En Revisión')
        RECHAZADO = 'RECHAZADO', _('Rechazado')

    # Relación con el usuario
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        related_name='analisis_propuestas',
        verbose_name=_('Usuario'),
        null=True,
        blank=True
    )
    
    # Información del usuario que se preserva incluso si el usuario es eliminado
    nombre_usuario = models.CharField(
        max_length=150,
        verbose_name=_('Nombre de Usuario'),
        blank=True,
        null=True,
        help_text=_('Nombre de usuario que creó el análisis')
    )
    
    email_usuario = models.EmailField(
        verbose_name=_('Email del Usuario'),
        blank=True,
        null=True,
        help_text=_('Email del usuario que creó el análisis')
    )

    # URL de la propuesta
    url_propuesta = models.URLField(
        max_length=500, 
        verbose_name=_('URL de Propuesta'),
        blank=True, 
        null=True
    )

    # Contenido del análisis
    contenido = models.TextField(
        verbose_name=_('Contenido del Análisis'),
        help_text=_('Descripción detallada del análisis de la propuesta')
    )

    # Prompts utilizados (JSONField para compatibilidad con datos existentes)
    prompts_utilizados = models.JSONField(
        verbose_name=_('Prompts Utilizados (JSON)'),
        blank=True, 
        null=True,
        help_text=_('Registro de prompts utilizados en el análisis (formato JSON)')
    )
    
    # Relación con prompts (para mejor integración)
    prompts = models.ManyToManyField(
        'Prompt',
        blank=True,
        related_name='analisis_propuestas',
        verbose_name=_('Prompts Utilizados')
    )

    # Fecha de análisis
    fecha_analisis = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_('Fecha de Análisis')
    )

    # Estado de la propuesta
    estado = models.CharField(
        max_length=20, 
        choices=Estado.choices, 
        default=Estado.BORRADOR,
        verbose_name=_('Estado')
    )

    # Metadatos adicionales
    fecha_ultima_modificacion = models.DateTimeField(
        auto_now=True, 
        verbose_name=_('Última Modificación')
    )

    # Campos opcionales
    palabras_clave = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name=_('Palabras Clave')
    )

    # Método para obtener resumen
    def get_resumen(self, longitud=100):
        """
        Obtener un resumen corto del contenido
        """
        return self.contenido[:longitud] + '...' if len(self.contenido) > longitud else self.contenido

    # Método para cambiar estado
    def cambiar_estado(self, nuevo_estado):
        """
        Cambiar el estado de la propuesta
        """
        if nuevo_estado in dict(self.Estado.choices):
            self.estado = nuevo_estado
            self.save()
        else:
            raise ValueError(_("Estado no válido"))

    def save(self, *args, **kwargs):
        """
        Sobrescribir método save para guardar información del usuario
        """
        # Si hay un usuario asociado, guardar su información
        if self.usuario and not self.nombre_usuario:
            self.nombre_usuario = self.usuario.username
            self.email_usuario = self.usuario.email
        
        super().save(*args, **kwargs)

    def __str__(self):
        if self.usuario:
            usuario_nombre = self.usuario.username
        else:
            usuario_nombre = self.nombre_usuario or "Usuario eliminado"
        return f"Análisis de Propuesta - {usuario_nombre} - {self.fecha_analisis.date()}"

    class Meta:
        verbose_name = _('Análisis de Propuesta')
        verbose_name_plural = _('Análisis de Propuestas')
        ordering = ['-fecha_analisis']
        indexes = [
            models.Index(fields=['usuario', 'fecha_analisis']),
            models.Index(fields=['estado'])
        ]
