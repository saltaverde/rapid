# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapid', '0007_datalayer_srid'),
    ]

    operations = [
        migrations.AddField(
            model_name='geoview',
            name='gs_uid',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='geoviewrole',
            name='role',
            field=models.IntegerField(default=2),
        ),
    ]
