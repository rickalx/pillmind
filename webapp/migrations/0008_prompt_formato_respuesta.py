from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0007_prompt_es_predeterminado'),
    ]

    operations = [
        migrations.AddField(
            model_name='prompt',
            name='formato_respuesta',
            field=models.TextField(blank=True, help_text='Estructura o formato que debe seguir la respuesta del modelo de IA', verbose_name='Formato de Respuesta'),
        ),
    ]
