# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rapid', '0005_auto_20160419_1617'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geoview',
            name='layers',
            field=models.ManyToManyField(to='rapid.DataLayer'),
        ),
    ]
