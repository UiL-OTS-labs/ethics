# -*- coding: utf-8 -*-
# Generated by Django 1.11.24 on 2019-12-12 09:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('observations', '0012_observation_has_advanced_consent_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='registration',
            name='requires_review',
            field=models.BooleanField(default=False),
        ),
    ]