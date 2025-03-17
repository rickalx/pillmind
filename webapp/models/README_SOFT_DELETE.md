# Implementación de Soft Delete en PillMind

Este documento describe la implementación del borrado lógico (soft delete) en los modelos de PillMind.

## Descripción General

Se ha implementado un sistema de borrado lógico basado en el enfoque "Paranoia", que permite marcar los registros como eliminados sin eliminarlos físicamente de la base de datos. Esto preserva la información histórica y permite restaurar registros si es necesario.

## Componentes Principales

### Modelo Base: `SoftDeleteModel`

- Ubicación: `pillmind/webapp/models/soft_delete.py`
- Proporciona la funcionalidad de borrado lógico a través de un modelo abstracto
- Añade un campo `deleted_on` que marca cuándo se eliminó un registro
- Incluye métodos para borrado lógico, restauración y borrado físico

### Managers Personalizados

1. **SoftDeleteManager (`objects`)**
   - Filtra automáticamente los objetos borrados lógicamente
   - Es el manager predeterminado para todos los modelos que heredan de `SoftDeleteModel`

2. **AllObjectsManager (`all_objects`)**
   - Permite acceder a todos los objetos, incluyendo los borrados lógicamente
   - Útil para auditoría, restauración y reportes históricos

### QuerySet Personalizado: `SoftDeleteQuerySet`

- Implementa operaciones de borrado lógico a nivel de queryset
- Permite borrar y restaurar múltiples objetos a la vez

## Modelos con Soft Delete

Los siguientes modelos implementan el borrado lógico:

1. `CustomUser`
2. `PerfilProfesional`
3. `AnalisisPropuesta`
4. `Prompt`
5. `HistorialModificacion`
6. `AutorInfo` (modelo interno de Prompt)

## Modelos sin Soft Delete

Los siguientes modelos de catálogo no implementan borrado lógico, ya que rara vez se eliminan:

1. `Especialidad`
2. `NivelAcceso`
3. `Rol`

## Uso

### Borrado Lógico

```python
# Borrado lógico de un objeto individual
usuario = CustomUser.objects.get(username='ejemplo')
usuario.delete()  # Marca como borrado, no elimina físicamente

# Borrado lógico de múltiples objetos
CustomUser.objects.filter(is_active=False).delete()  # Marca todos como borrados
```

### Consultas

```python
# Obtener solo objetos no borrados (comportamiento predeterminado)
usuarios_activos = CustomUser.objects.all()  # No incluye borrados

# Obtener todos los objetos, incluyendo los borrados
todos_usuarios = CustomUser.all_objects.all()  # Incluye borrados

# Obtener solo objetos borrados
usuarios_borrados = CustomUser.all_objects.filter(deleted_on__isnull=False)
```

### Restauración

```python
# Restaurar un objeto individual
usuario = CustomUser.all_objects.get(username='ejemplo')
usuario.undelete()  # Restaura el objeto

# Restaurar múltiples objetos
CustomUser.all_objects.filter(deleted_on__isnull=False).undelete()
```

### Borrado Físico (cuando sea absolutamente necesario)

```python
# Borrado físico de un objeto individual
usuario = CustomUser.all_objects.get(username='ejemplo')
usuario.hard_delete()  # Elimina físicamente

# Borrado físico de múltiples objetos
CustomUser.all_objects.filter(deleted_on__isnull=False).hard_delete()
```

## Consideraciones

1. **Consultas Existentes**: Las consultas existentes seguirán funcionando sin cambios, ya que el manager predeterminado filtra automáticamente los objetos borrados.

2. **Relaciones**: El borrado lógico no se propaga automáticamente a las relaciones. Si se requiere este comportamiento, debe implementarse manualmente.

3. **Rendimiento**: El filtrado adicional puede tener un impacto mínimo en el rendimiento de las consultas, pero es insignificante en comparación con los beneficios de preservar los datos.

4. **Índices**: Se recomienda crear índices en el campo `deleted_on` si se realizan consultas frecuentes que filtren por este campo.

## Pasos para Completar la Implementación

Para completar la implementación del soft delete, es necesario:

1. Generar las migraciones:
   ```
   python manage.py makemigrations webapp
   ```

2. Aplicar las migraciones:
   ```
   python manage.py migrate webapp
   ```

Estos pasos crearán la columna `deleted_on` en las tablas correspondientes a los modelos que heredan de `SoftDeleteModel`.
