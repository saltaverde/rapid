from django.core.management import BaseCommand
import time

from rapid.exporter import Exporter
from rapid.select import *
from rapid.helpers import *
from rapid.models import *
from rapid.importer import *


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.say_hi()
        return
        GeoView.objects.all().delete()
        ApiToken.objects.all().delete()
        DataLayer.objects.all().delete()
        return

        path = '/home/dotproj/djangostack-1.7.8-0/apps/django/django_projects/pipelion/data/dropbox/sf-bay.zip'

        filename = os.path.basename(path)
        filename = os.path.splitext(filename)[0]

        DataLayer.objects.all().delete()

        data = DataOperator('974bdff1e307fa4506e69b810db04ac709d99796')
        uid = data.create_layer(filename + '_' + str(int(time.time())), True, properties=None)

        importer = Importer('974bdff1e307fa4506e69b810db04ac709d99796')
        importer.import_shapefile(path, layer_uid=uid)
        return
        # uid = 'fRqJo7azWgpGoMnzShjvq5'
        exporter = Exporter('974bdff1e307fa4506e69b810db04ac709d99796')
        exporter.export_shapefile(data.get_layer(uid).feature_set.all())


    def say_hi(self):
        print "Hello world"
        print ''

    def alexa_things(self):
        url = 'http://pipelions.com/rapid/geoview/'
      #  payload = '{ "des": "California Cities", "public": true, "props": {} }'
        payload = '{ "geom": { "coordinates": [ [ [ -121.581354, 36.899152 ], [ -121.581154, 36.919252 ], [ -121.624755, 36.940451 ], [ -121.645791, 36.93233 ], [ -121.654038, 36.950584 ], [ -121.66613, 36.96434 ], [ -121.693303, 36.96823 ], [ -121.695358, 36.98515 ], [ -121.717878, 36.995561 ], [ -121.738627, 36.990085 ], [ -121.718762, 37.007557 ], [ -121.736186, 37.015342 ], [ -121.75562, 37.0491 ], [ -121.809185, 37.069369 ], [ -121.82402, 37.08757 ], [ -121.99109, 37.14427 ], [ -122.015966, 37.165658 ], [ -122.055064, 37.212683 ], [ -122.08981, 37.22327 ], [ -122.152278, 37.286055 ], [ -122.154381, 37.290423 ], [ -122.162209, 37.293656 ], [ -122.165375, 37.296342 ], [ -122.163627, 37.301257 ], [ -122.16823, 37.307807 ], [ -122.17703, 37.312501 ], [ -122.186058, 37.314341 ], [ -122.18734, 37.321535 ], [ -122.184187, 37.325674 ], [ -122.184078, 37.334842 ], [ -122.189767, 37.341497 ], [ -122.197131, 37.352206 ], [ -122.202102, 37.364788 ], [ -122.199288, 37.373563 ], [ -122.193099, 37.382737 ], [ -122.190064, 37.391148 ], [ -122.191779, 37.399802 ], [ -122.193827, 37.411275 ], [ -122.189162, 37.418923 ], [ -122.190423, 37.426335 ], [ -122.185924, 37.433648 ], [ -122.179412, 37.440368 ], [ -122.174787, 37.443861 ], [ -122.167874, 37.44958 ], [ -122.1629, 37.453542 ], [ -122.155715, 37.454907 ], [ -122.150158, 37.457129 ], [ -122.141065, 37.457133 ], [ -122.131827, 37.453782 ], [ -122.126813, 37.453533 ], [ -122.122866, 37.457278 ], [ -122.111974, 37.466438 ], [ -122.081473, 37.477838 ], [ -122.045271, 37.460276 ], [ -121.996671, 37.467239 ], [ -121.975071, 37.460639 ], [ -121.947087, 37.467424 ], [ -121.925548, 37.454389 ], [ -121.855762, 37.484537 ], [ -121.472648, 37.48217 ], [ -121.486775, 37.475652 ], [ -121.462917, 37.451489 ], [ -121.472606, 37.423345 ], [ -121.448163, 37.391677 ], [ -121.42405, 37.393635 ], [ -121.412549, 37.389435 ], [ -121.42365, 37.358837 ], [ -121.40915, 37.330637 ], [ -121.405753, 37.31099 ], [ -121.459068, 37.282319 ], [ -121.45575, 37.24944 ], [ -121.441746, 37.231127 ], [ -121.422711, 37.22236 ], [ -121.399451, 37.150386 ], [ -121.383551, 37.151487 ], [ -121.384552, 37.165507 ], [ -121.354561, 37.183893 ], [ -121.328409, 37.16595 ], [ -121.29773, 37.166429 ], [ -121.281107, 37.183603 ], [ -121.262293, 37.159473 ], [ -121.237712, 37.15758 ], [ -121.226804, 37.134774 ], [ -121.217339, 37.123042 ], [ -121.230439, 37.096942 ], [ -121.245384, 37.089501 ], [ -121.209637, 37.068243 ], [ -121.208198, 37.061289 ], [ -121.223387, 37.057507 ], [ -121.224507, 37.039743 ], [ -121.245989, 37.025575 ], [ -121.233137, 36.999346 ], [ -121.245887, 36.983036 ], [ -121.215406, 36.961248 ], [ -121.418253, 36.96064 ], [ -121.451972, 36.98884 ], [ -121.463561, 36.978294 ], [ -121.488949, 36.983148 ], [ -121.501488, 36.971895 ], [ -121.513813, 36.945155 ], [ -121.558452, 36.910468 ], [ -121.560272, 36.897111 ], [ -121.581354, 36.899152 ] ] ], "type": "Polygon" }, "des": "Santa Clara County, CA", "props": null }'
        #        payload = payload.replace(u"\xe2", u"")
        print payload
        r = requests.post(url, data=payload)

        print r.text
        pass

    def testwoo(self):
        # try:
        #     from osgeo import ogr, osr, gdal
        # except:
        #     sys.exit('ERROR: cannot find GDAL/OGR modules')

        # self.esriprj2standards('/home/dotproj/djangostack-1.7.8-0/apps/django/django_projects/pipelion/data/samples/WA/WA_Cowlitz_StreetCenterlines/StreetCenterlines.prj')
        return

    def create_region(self):
        url = 'http://pipelions.com/rapid/create/region/'
        slo = GeoView.objects.get(descriptor='San Luis Obispo')
        # { "type": "Polygon", "coordinates": [ [ [ -94.913890, 42.909700 ], [ -94.913723, 43.255054 ], [ -94.443137, 43.255014 ], [ -94.442954, 42.908073 ], [ -94.913890, 42.909700 ] ] ] } }
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

