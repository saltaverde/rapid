from django.core.management import BaseCommand
import json
import geojson
from pprint import pprint
import urllib2
from rapid.models import GeoView, Feature
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point
import geojson
import requests


class Command(BaseCommand):
    def create_region(self):
        url = 'http://pipelions.com/rapid/create/region/'
        slo = GeoView.objects.get(descriptor='San Luis Obispo')
#{ "type": "Polygon", "coordinates": [ [ [ -94.913890, 42.909700 ], [ -94.913723, 43.255054 ], [ -94.443137, 43.255014 ], [ -94.442954, 42.908073 ], [ -94.913890, 42.909700 ] ] ] } }
       # payload = '{"geom": { "type": "Polygon", "coordinates": [ [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ] ] }, "des": "TestRegion", "uid": "slo"}'
 #       payload = '{"geom": { "type": "Polygon", "coordinates": [ [ [ -94.913890, 42.909700 ], [ -94.913723, 43.255054 ], [ -94.443137, 43.255014 ], [ -94.442954, 42.908073 ], [ -94.913890, 42.909700 ] ] ] }, "des": "TestRegion", "uid": "slo"}'
        payload = '{"geom": { "type": "Polygon", "coordinates": [ [ [-120.680433, 35.312359], [-120.664811, 35.312429], [-120.655284, 35.308542], [-120.650521, 35.299786], [-120.653181, 35.296056], [-120.665005, 35.296494], [-120.666571, 35.302623], [-120.673695, 35.298526], [-120.680776, 35.308157], [-120.680433, 35.312359] ] ] }, "des": "TodaysTestRegion", "uid": "newCalPoly"}'

#        payload = {'geom': '{ "type": "Polygon", "coordinates": [ [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ] ] }', 'des': 'TestRegion', 'uid': 'slo'}
        r = requests.post(url, data=payload)
       # ?geom=POLYGON((0%200,%205%205,%203%203,%200%200))&des=testingcreateregion&uid=SLO
        print r.text



    def populate_usgs(self):
        endpoint = 'http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_week.geojson'
        f = urllib2.urlopen(endpoint)
        content = f.read()
        data = geojson.loads(content)
        Feature.objects.all().delete()
        for feature in data.features:

            entry = Feature()

            out = str(feature.geometry)
            geom = GEOSGeometry(out)

            if isinstance(geom, Point):
                geom = Point(geom[0], geom[1])

            entry.geom = geom
            entry.internet_media_type = 'application/vnd.geo+json'

            entry.save()

    def handle(self, *args, **options):


        self.create_region()

       # self.populate_usgs()


