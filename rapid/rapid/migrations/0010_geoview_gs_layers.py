# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapid', '0009_auto_20160807_0024'),
    ]

    operations = [
        migrations.AddField(
            model_name='geoview',
            name='gs_layers',
            field=models.TextField(null=True),
        ),
    ]
