# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-30 00:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='time_stamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
