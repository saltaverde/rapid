# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapid', '0004_userprofile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datalayer',
            name='include_features',
            field=models.BooleanField(default=True),
        ),
    ]
