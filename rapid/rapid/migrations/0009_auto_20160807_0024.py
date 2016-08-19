# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapid', '0008_auto_20160807_0021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoviewrole',
            name='role',
            field=models.IntegerField(default=0),
        ),
    ]
