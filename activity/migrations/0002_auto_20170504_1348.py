# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='action',
            name='created',
            field=models.DateTimeField(db_index=True, default=django.utils.timezone.now),
        ),
    ]
