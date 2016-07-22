from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.gdal import DataSource as GdalDataSource
from django.contrib.gis.gdal import SpatialReference
from django.core.files.base import ContentFile, File

from rapid.helpers import *
from rapid.models import *
from rapid.select import *
from rapid.settings import TEMP_DATA_DIR

import geojson
import urllib2
from zipfile import *
from StringIO import StringIO
import os

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

    def import_document_url(self, url, geom, layer_uid=None):
        '''CAUTION: UNTESTED!'''
        with urllib2.urlopen(url) as f:
            content = f.read()

        geom = Point(geom[0], geom[1])

        baseurl, filename = os.path.split(endpoint)
        filename, ext = os.path.splitext(filename)

        self.import_document_content(content, filename, geom, layer_uid)

    def import_document_content(self, content, filename, geom, layer_uid=None):
        '''CAUTION: UNTESTED!'''
        try:
            data = DataOperator(self.token_key)
            layer = data.get_layer(layer_uid)
        except:
            raise Exception('Invalid layer UID')

        with ContentFile(content) as f:
            f.name = filename
            data.create_feature(geom=geom, layer=layer, properties=None, file=f)

    def import_document(self, path, geom, layer_uid=None):
        '''CAUTION: UNTESTED!'''
        try:
            data = DataOperator(self.token_key)
            layer = data.get_layer(layer_uid)
        except:
            raise Exception('Invalid layer UID')

        geom = Point(geom[0], geom[1])

        with open(path, 'r') as f:
            data.create_feature(geom=geom, layer=layer, properties=None, file=f)

        os.remove(path)

    def import_shapefile_url(self, endpoint, layer_uid=None):
        '''
        CAUTION: UNTESTED!
        '''
        f = urllib2.urlopen(endpoint)

        # Following step could take awhile
        content = f.read()

        baseurl, filename = os.path.split(endpoint)
        filename, ext = os.path.splitext(filename)

        self.import_shapefile_content(content, filename, layer_uid)

    def import_shapefile_content(self, content, filename, layer_uid=None):
        try:
            data = DataOperator(self.token_key)
            layer = data.get_layer(layer_uid)
        except:
            raise Exception('Invalid layer UID')

        new_dir = filename + '_' + str(int(time.time()))

        location = os.path.join(TEMP_DATA_DIR, new_dir)

        with ZipFile(StringIO(content)) as z:
            z.extractall(location)

        shp_matches = []
        prj_matches = []

        for root, dirnames, filenames in os.walk(location):
            for filename in fnmatch.filter(filenames, '*.shp'):
                shp_matches.append(os.path.join(root, filename))
            for filename in fnmatch.filter(filenames, '*.prj'):
                prj_matches.append(os.path.join(root, filename))

        if len(shp_matches) == 0:
            raise Exception('Unable to read Shapefile (.shp file not found in archive)')

        shp_location = shp_matches[0]

        srid = 4326

        if len(prj_matches) > 0:
            prj_location = prj_matches[0]
            prj_content = open(prj_location, 'r').read().strip()
            srid = prj_content_to_srid(prj_content)

        sf = shapefile.Reader(shp_location)

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
                record_entry = record[i - 1]

                if type(record_entry) is str:
                    if record_entry.isspace():
                        properties[sf.fields[i][0]] = None
                    else:
                        properties[sf.fields[i][0]] = record_entry
                else:
                    properties[sf.fields[i][0]] = record_entry

            if 'ORIGID' in properties:
                del properties['ORIGID']
            properties = to_json(properties)

            data.create_feature(geom, layer=layer, properties=properties)

        return

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
            for filename in fnmatch.filter(filenames, '*.shp'):
                shp_matches.append(os.path.join(root, filename))
            for filename in fnmatch.filter(filenames, '*.prj'):
                prj_matches.append(os.path.join(root, filename))

        if len(shp_matches) == 0:
            raise Exception('Unable to read Shapefile (.shp file not found in archive)')

        shp_location = shp_matches[0]

        srid = 4326

        if len(prj_matches) > 0:
            prj_location = prj_matches[0]
            prj_content = open(prj_location, 'r').read().strip()
            srid = prj_content_to_srid(prj_content)

        sf = shapefile.Reader(shp_location)

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
                record_entry = record[i - 1]

                if type(record_entry) is str:
                    if record_entry.isspace():
                        properties[sf.fields[i][0]] = None
                    else:
                        properties[sf.fields[i][0]] = record_entry
                else:
                    properties[sf.fields[i][0]] = record_entry

            if 'ORIGID' in properties:
                del properties['ORIGID']
            properties = to_json(properties)

            data.create_feature(geom, layer=layer, properties=properties)

        return

'''
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
            srid = srs.srid

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

                geom = transform_wkt(feat.geom.wkt, srid, 4326)

                properties = to_json(properties)

                data.create_feature(geom, layer=layer, properties=properties)

        else:
            print 'No data imported. The Shapefile {0} has no records (features).'.format(shp_location)

        return
 '''