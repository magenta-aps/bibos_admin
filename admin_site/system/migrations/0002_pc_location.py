# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pc',
            name='location',
            field=models.CharField(default=b'', max_length=1024, verbose_name='location', blank=True),
        ),
    ]
