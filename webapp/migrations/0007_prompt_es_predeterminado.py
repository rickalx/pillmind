# Generated by Django 5.1.7 on 2025-03-18 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0006_alter_prompt_autor_info'),
    ]

    operations = [
        migrations.AddField(
            model_name='prompt',
            name='es_predeterminado',
            field=models.BooleanField(default=False, help_text='Si está marcado, este prompt se utilizará por defecto en el chatbot', verbose_name='Es predeterminado para chatbot'),
        ),
    ]
