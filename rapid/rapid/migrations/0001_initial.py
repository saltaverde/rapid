# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApiToken',
            fields=[
                ('uid', models.TextField(serialize=False, primary_key=True)),
                ('key', models.TextField(unique=True, db_index=True)),
                ('descriptor', models.TextField(unique=True)),
                ('issued', models.TimeField(auto_now_add=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataLayer',
            fields=[
                ('uid', models.TextField(serialize=False, primary_key=True)),
                ('descriptor', models.TextField()),
                ('properties', models.TextField(null=True)),
                ('is_public', models.BooleanField(default=False)),
                ('include_features', models.NullBooleanField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataLayerRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.IntegerField(default=0)),
                ('layer', models.ForeignKey(to='rapid.DataLayer')),
                ('token', models.ForeignKey(to='rapid.ApiToken')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField(null=True)),
                ('update_interval', models.TimeField(null=True)),
                ('expected_type', models.TextField(null=True)),
                ('properties', models.TextField(null=True)),
                ('layer', models.ForeignKey(to='rapid.DataLayer', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Feature',
            fields=[
                ('uid', models.TextField(serialize=False, primary_key=True)),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True)),
                ('bbox', django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True)),
                ('properties', models.TextField(null=True)),
                ('create_timestamp', models.TimeField(db_index=True, auto_now_add=True, null=True)),
                ('hash', models.TextField(unique=True, null=True, db_index=True)),
                ('modified_timestamp', models.TimeField(auto_now=True, null=True)),
                ('layer', models.ForeignKey(to='rapid.DataLayer', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeoView',
            fields=[
                ('uid', models.TextField(serialize=False, primary_key=True)),
                ('descriptor', models.TextField()),
                ('geom', django.contrib.gis.db.models.fields.GeometryField(srid=4326, null=True)),
                ('bbox', django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True)),
                ('properties', models.TextField(null=True)),
                ('is_public', models.BooleanField(default=False)),
                ('include_layers', models.NullBooleanField()),
                ('include_geom', models.NullBooleanField()),
                ('layers', models.ManyToManyField(to='rapid.DataLayer', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GeoViewRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.IntegerField(default=0)),
                ('geo_view', models.ForeignKey(to='rapid.GeoView')),
                ('token', models.ForeignKey(to='rapid.ApiToken')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
