from django.contrib.gis.geos import GEOSGeometry, Point, Polygon
from django.core.management import BaseCommand
import rapid
from django.contrib.gis.db import models
import urllib2
import json
import requests

class Command(BaseCommand):
    def handle(self, *args, **options):
        print "Hello world"
        payload = {'key1': 'value1', 'key2': 'value2'}
        r = requests.get('http://pipelions.com/rapid/regions', params=payload)
        print(r.url)
        # region = rapid.models.Region()
        # region.description = "hello world"
        # region.geom = GEOSGeometry('POINT(-97.309990 30.111199)')
        # region.name = "regionName"
        # region.uid = '111'
        # region.bbox = GEOSGeometry('POLYGON((0 0, 5 5, 3 3, 0 0))')
        # region.save()
