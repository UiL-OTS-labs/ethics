# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-01 11:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0006_auto_20180808_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='continuation',
            field=models.PositiveIntegerField(choices=[(0, 'Goedkeuring door FETC-GW'), (1, 'Revisie noodzakelijk'), (2, 'Afwijzing door FETC-GW'), (3, 'Open review met lange (4-weken) route'), (4, 'Laat opnieuw beoordelen door METC')], default=0, verbose_name='Afhandeling'),
        ),
    ]