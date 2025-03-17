from django.db import models
from django.utils import timezone
from django.db.models.query import QuerySet

class SoftDeleteQuerySet(QuerySet):
    """
    QuerySet personalizado que previene el borrado físico de objetos.
    En su lugar, establece el campo `deleted_on`, efectivamente realizando un borrado lógico.
    """
    def delete(self):
        """
        Sobrescribe el método delete para realizar un borrado lógico en lugar de físico.
        """
        for obj in self:
            obj.deleted_on = timezone.now()
            obj.save()

    def undelete(self):
        """
        Método para restaurar objetos borrados lógicamente.
        """
        for obj in self:
            obj.deleted_on = None
            obj.save()

    def hard_delete(self):
        """
        Método para realizar un borrado físico cuando sea absolutamente necesario.
        """
        return super().delete()


class SoftDeleteManager(models.Manager):
    """
    Manager personalizado que solo expone objetos que NO han sido borrados lógicamente.
    """
    def get_queryset(self):
        """
        Sobrescribe el método get_queryset para filtrar objetos borrados.
        """
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            deleted_on__isnull=True
        )


class AllObjectsManager(models.Manager):
    """
    Manager que expone todos los objetos, incluyendo los borrados lógicamente.
    """
    def get_queryset(self):
        """
        Retorna todos los objetos sin filtrar por deleted_on.
        """
        return SoftDeleteQuerySet(self.model, using=self._db)


class SoftDeleteModel(models.Model):
    """
    Modelo base abstracto que implementa la funcionalidad de borrado lógico.
    Los modelos que hereden de esta clase tendrán la capacidad de ser borrados lógicamente.
    """
    deleted_on = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Fecha de eliminación",
        help_text="Fecha y hora en que el objeto fue eliminado lógicamente."
    )

    # Manager predeterminado que filtra objetos borrados
    objects = SoftDeleteManager()
    
    # Manager para acceder a todos los objetos, incluyendo los borrados
    all_objects = AllObjectsManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """
        Sobrescribe el método delete para realizar un borrado lógico.
        """
        self.deleted_on = timezone.now()
        self.save(using=using)

    def undelete(self, using=None):
        """
        Método para restaurar un objeto borrado lógicamente.
        """
        self.deleted_on = None
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        """
        Método para realizar un borrado físico cuando sea absolutamente necesario.
        """
        return super().delete(using=using, keep_parents=keep_parents)
