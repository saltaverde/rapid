from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.gdal import DataSource as GdalDataSource
from django.contrib.gis.gdal import SpatialReference

from rapid.helpers import *
from rapid.models import *
from rapid.select import *
from rapid.settings import TEMP_DATA_DIR

import geojson
import urllib2

class Importer(object):
    def __init__(self, token_key=None):
        self.token_key = token_key

    def import_geojson_file(self, filepath, layer_uid=None):
        content = open(filepath).read()
        self.import_geojson_content(content, layer_uid)

    def import_geojson_url(self, endpoint, layer_uid=None):
        f = urllib2.urlopen(endpoint)
        content = f.read()
        self.import_geojson_content(content, layer_uid)

    def import_geojson_content(self, content, layer_uid=None):
        try:
            data = DataOperator(self.token_key)
            layer = data.get_layer(layer_uid)
        except:
            raise Exception('Invalid layer UID')

        data = geojson.loads(content)

        for feature in data.features:

            out = str(feature.geometry)
            geom = GEOSGeometry(out)

            if isinstance(geom, Point):
                geom = Point(geom[0], geom[1])

            data.create_feature(geom, layer=layer, properties=feature.properties)

    def import_kml(self, path, layer_uid=None):

        try:
            data = DataOperator(self.token_key)
            layer = data.get_layer(layer_uid)
        except:
            raise Exception('Invalid layer UID')

        ds = GdalDataSource(path)


    def import_shapefile(self, path, layer_uid=None):

        try:
            data = DataOperator(self.token_key)
            layer = data.get_layer(layer_uid)
        except:
            raise Exception('Invalid layer UID')

        try:
            new_dir, filename = unzip_from(path)
        except:
            raise Exception('Unable to extract Shapefile')

        location = os.path.join(TEMP_DATA_DIR, new_dir)

        shp_matches = []
        prj_matches = []

        for root, dirnames, filenames in os.walk(location):
            for filename in fnmatch.filter(filenames, '[!.]*.shp'):
                shp_matches.append(os.path.join(root, filename))
            for filename in fnmatch.filter(filenames, '[!.]*.prj'):
                prj_matches.append(os.path.join(root, filename))

        if len(shp_matches) == 0:
            raise Exception('Unable to read Shapefile (No .shp file not found in archive)')

        shp_location = shp_matches[0]

        srid = None

        if len(prj_matches) > 0:
            ds = GdalDataSource(shp_location)
            lyr = ds[0]
            srs = SpatialReference(lyr.srs.proj4)
            srid = srs['AUTHORITY', 1]

        if srid is None:
            print "Unable to locate EPSG authority code for {0}. Using 4326.".format(srs.name)
            srid = 4326

        # update srid in DB
        layer.srid = srid
        layer.save()

        # ct = CoordTransform(srs, SpatialReference('WGS84'))
        if lyr.num_feat > 0:
            for feat in lyr:
                properties = {}

                for field in feat.fields:
                    temp = feat.get(field)
                    if type(data) is str:
                        if data.isspace():
                            properties[field] = None
                        else:
                            properties[field] = temp
                    else:
                        properties[field] = temp

                geom = GEOSGeometry(feat.geom.wkt)
                properties = to_json(properties)

                data.create_feature(geom, layer=layer, properties=properties)

        else:
            print 'No data imported. The Shapefile {0} has no records (features).'.format(shp_location)

        return

'''
        sf = shapefile.Reader(shp_location)

        if sf.numRecords > 0:
            for shape_record in sf.shapeRecords():
                geom_type = shape_record.shape.__geo_interface__['type']
                coords = shape_record.shape.points

                try:
                    parts = shape_record.shape.parts
                except:
                    parts = None

                wkt = create_wkt(geom_type, coords, parts)
                results = transform_wkt(wkt, srid, 4326)

                geom = GEOSGeometry(results)

                if isinstance(geom, Point):
                    geom = Point(geom[0], geom[1])

                record = shape_record.record

                properties = {}
                for i in xrange(1, len(sf.fields)):
 '''