from django.core.management import BaseCommand
import json
import geojson
from pprint import pprint
import urllib2
from rapid.database.select import import_geojson_url, import_geojson_file
from rapid.models import GeoView, Feature, Archive, DataLayer
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point
import geojson


class Command(BaseCommand):

    def populate_geojson_urls(self):
        endpoint = 'http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/1.0_week.geojson'
        descriptor = "Earthquakes"
        import_geojson_url(descriptor, endpoint)

        endpoint = 'http://catalog.opendata.city/dataset/3645b173-b7c6-40f6-ad3a-32c9972bb17c/resource/5d933d37-5cbf-4d9f-aded-b3bacb1dd1ab/download/temp.geojson'
        descriptor = "Washington Cities"
        import_geojson_url(descriptor, endpoint)

        endpoint = 'http://catalog.opendata.city/dataset/425bd9d9-f9f8-441c-92d6-3022b907be84/resource/919bbd6c-f880-459d-abcc-4d781dbde59b/download/temp.geojson'
        descriptor = "California Cities"
        import_geojson_url(descriptor, endpoint)


    def populate_counties(self):
        filepath = 'data/geojson_borders/counties.geojson'
        descriptor = "US Counties"
        import_geojson_file(descriptor, filepath)

        filepath = 'data/street_lines.geojson'
        descriptor = "Washington Street Lines"
        import_geojson_file(descriptor, filepath)

    def handle(self, *args, **options):

        DataLayer.objects.all().delete()
        Feature.objects.all().delete()
        GeoView.objects.all().delete()

        self.populate_counties()
        self.populate_geojson_urls()


