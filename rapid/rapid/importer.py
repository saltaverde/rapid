from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.gdal import DataSource as GdalDataSource
import geojson
import urllib2
from rapid.helpers import *
from rapid.models import *
from rapid.select import *
from rapid.settings import TEMP_DATA_DIR

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
            raise Exception('Unable to read Shapefile (.shp file not found in archive)')

        shp_location = shp_matches[0]

        srid = None

        if len(prj_matches) > 0:
            ds = GdalDataSource(shp_location)
            lyrs = [lyr for lyr in ds]
            srid = lyrs[0].srs.srid

        if srid is None:
            print "Unable to locate EPSG for %s. Using 4326.".format(lyrs[0].srs.name)
            srid = 4326

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

        else:
            print "No data imported. The shapefile has no records (features)."