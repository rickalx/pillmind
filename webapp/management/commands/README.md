# Migración de Datos de Prompts

Este directorio contiene un comando de gestión de Django para migrar datos de prompts desde el campo `prompts_utilizados` (JSONField) al nuevo campo `prompts` (ManyToManyField) en el modelo `AnalisisPropuesta`.

## Contexto

Anteriormente, los prompts utilizados en los análisis de propuestas se almacenaban como datos JSON en el campo `prompts_utilizados`. Con la introducción del modelo `Prompt`, ahora es posible establecer relaciones directas entre análisis y prompts, lo que proporciona varias ventajas:

- Mejor integridad referencial
- Consultas más eficientes
- Reutilización de prompts entre diferentes análisis
- Seguimiento de versiones y modificaciones de prompts

## Pasos para Aplicar los Cambios

### 1. Aplicar Migraciones

Primero, es necesario aplicar las migraciones para actualizar el esquema de la base de datos:

```bash
cd pillmind
python manage.py makemigrations
python manage.py migrate
```

### 2. Ejecutar el Comando de Migración de Datos

El comando `migrate_prompts_data` analiza todos los registros de `AnalisisPropuesta` que tienen datos en el campo `prompts_utilizados` y crea los correspondientes objetos `Prompt`, estableciendo las relaciones adecuadas.

#### Modo Simulación (Recomendado para Verificación)

Primero, ejecute el comando en modo simulación para verificar qué cambios se realizarán sin modificar la base de datos:

```bash
python manage.py migrate_prompts_data --dry-run
```

#### Ejecución Real

Una vez verificado que todo está correcto, ejecute el comando sin la opción `--dry-run` para realizar la migración:

```bash
python manage.py migrate_prompts_data
```

### 3. Verificación

Después de ejecutar el comando, verifique que los datos se hayan migrado correctamente:

```bash
python manage.py shell
```

```python
from webapp.models import AnalisisPropuesta, Prompt

# Verificar cuántos prompts se han creado
print(f"Total de prompts: {Prompt.objects.count()}")

# Verificar cuántos análisis tienen prompts relacionados
print(f"Análisis con prompts: {AnalisisPropuesta.objects.filter(prompts__isnull=False).distinct().count()}")

# Comparar con los análisis que tienen prompts_utilizados
print(f"Análisis con prompts_utilizados: {AnalisisPropuesta.objects.exclude(prompts_utilizados__isnull=True).exclude(prompts_utilizados={}).count()}")
```

## Consideraciones

- El comando mantiene el campo `prompts_utilizados` intacto para mantener compatibilidad con código existente.
- Si un prompt con el mismo texto ya existe, se reutiliza en lugar de crear uno nuevo.
- El comando maneja diferentes formatos de datos en el campo `prompts_utilizados` (diccionarios, listas, etc.).
- Se utiliza transacción atómica para garantizar la integridad de los datos durante la migración.
- El campo `rol_ia` no se asigna automáticamente durante la migración y debe ser configurado manualmente después.
- Todos los prompts migrados se crean con estado `BORRADOR` por defecto y deben ser revisados manualmente.

## Actualización de Código Existente

Después de la migración, se recomienda actualizar el código existente para utilizar la nueva relación `prompts` en lugar de `prompts_utilizados`. Por ejemplo:

```python
# Antes
prompts_json = analisis.prompts_utilizados
if prompts_json:
    # Procesar datos JSON...

# Después
prompts = analisis.prompts.all()
for prompt in prompts:
    # Usar directamente los objetos Prompt
    objetivo = prompt.objetivo
    texto = prompt.texto
    # ...
