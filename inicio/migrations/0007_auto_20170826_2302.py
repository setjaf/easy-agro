# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-27 04:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inicio', '0006_auto_20170826_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productocampo',
            name='fecha_recepcion',
            field=models.DateTimeField(null=True, verbose_name='dia_creado'),
        ),
    ]
