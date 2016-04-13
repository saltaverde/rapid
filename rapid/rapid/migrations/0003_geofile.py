# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rapid', '0002_geoview_token_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeoFile',
            fields=[
                ('uid', models.TextField(serialize=False, primary_key=True)),
                ('content', models.BinaryField(null=True)),
                ('filename', models.TextField(null=True)),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True)),
                ('descriptor', models.TextField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
