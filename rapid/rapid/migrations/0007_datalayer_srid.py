# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapid', '0006_auto_20160419_1618'),
    ]

    operations = [
        migrations.AddField(
            model_name='datalayer',
            name='srid',
            field=models.TextField(null=True),
        ),
    ]
