# Generated by Django 5.1.7 on 2025-03-18 16:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0005_alter_prompt_etiquetas'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prompt',
            name='autor_info',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='webapp.autorinfo', verbose_name='Información de Autor'),
        ),
    ]
