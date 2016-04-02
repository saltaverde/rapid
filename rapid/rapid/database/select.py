import fnmatch
import geojson
import os
import shapefile
import shortuuid
import urllib2
from rapid.api.ingest import unzip_from
from rapid.helpers import *
from rapid.models import GeoView, DataLayer, Feature, ApiToken
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point
import json

# FEATURES
def create_feature(geom, layer=None, archive=None, properties=None, Token=None):
    feature = Feature(layer=layer, geom=geom)
    feature.uid = get_uid()
    if properties:
        feature.properties = properties
    feature.save()
    return feature.uid

def delete_geoview(uid, Token=None):
    try:
        GeoView.objects.get(uid=uid).delete()
        return True
    except:
        return False

def delete_layer(uid, Token=None):
    try:
        DataLayer.objects.get(uid=uid).delete()
        return True
    except:
        return False

def delete_feature(uid, Token=None):
    try:
        Feature.objects.get(uid=uid).delete()
        return True
    except:
        return False

def update_feature(uid, geom, layer=None, archive=None, properties=None, Token=None):
    feature = get_feature(uid)
    feature.geom = geom
    feature.layer = layer
    if properties:
        feature.properties = properties
    feature.archive = archive
    feature.save()
    return feature.uid


def get_feature(uid, Token=None):
    feature = Feature.objects.filter(uid=uid)[0]
    return feature


# LAYERS
def create_layer(descriptor, is_public, properties, Token=None):
    layer = DataLayer(descriptor=descriptor, properties=properties, is_public=is_public)
    layer.uid = get_uid()
    layer.save()
    return layer.uid


def get_layers(Token=None):
    return DataLayer.objects.all()
    pass


def get_layer(uid, start=None, stop=None, Token=None):
    layer = DataLayer.objects.filter(uid=uid)
    if start and stop:
        layer = layer.feature_set.filter(create_timestamp__lte=start, create_timestamp__gte=stop)
    elif start:
        layer = layer.feature_set.filter(create_timestamp__lte=start)
    elif stop:
        layer = layer.feature_set.filter(create_timestamp__gte=stop)
    return layer[0]
    pass


# GEOVIEWS
def create_geoview(geom, descriptor, properties, token=None):
    view = GeoView(geom=geom, descriptor=descriptor, properties=properties)
    view.uid = get_uid()
    view.save()
    return view.uid


def get_geoviews(Token=None):
    return list(GeoView.objects.all())


def get_geoview(uid, file=False, Token=None):
    if not file:
        geoview = GeoView.objects.filter(uid=uid)[0]
        return geoview
    else:
        return "somefile.geojson"


def add_layer_to_geoview(geoview_uid, layer_uid, Token=None):
    geoview = GeoView.objects.filter(uid=geoview_uid)
    layer = DataLayer.objects.filter(uid=layer_uid)

    if geoview.count() > 0 and layer.count() > 0:
        geoview[0].add_layer(layer[0])
        geoview[0].save()
        return "SUCCESS: ", geoview[0].uid, " + ", layer[0].uid
    return "FAILURE: incorrect uid"


def remove_layer_from_geoview(layer_uid, geoview_uid, Token=None):
    geoview = GeoView.objects.filter(uid=geoview_uid)
    layer = DataLayer.objects.filter(uid=layer_uid)

    # make sure only one geoview and layer
    if geoview.count() > 0 and layer.count() > 0:
        geoview[0].remove_layer(layer[0])
        geoview[0].save()
        return "SUCCESS: ", geoview[0].uid, " + ", layer[0].uid
    return "FAILURE: incorrect uid"


# HELPERS
def import_geojson_file(descriptor, filepath, Token=None):
    content = open(filepath).read()
    import_geojson_content(content, descriptor)


def import_geojson_url(descriptor, endpoint, Token=None):
    f = urllib2.urlopen(endpoint)
    content = f.read()
    import_geojson_content(content, descriptor)


def import_geojson_content(content, descriptor, Token=None):
    mime = 'application/vnd.geo+json'

    layer = DataLayer()
    layer.descriptor = descriptor
    layer.uid = get_uid()
    layer.save()

    data = geojson.loads(content)

    for feature in data.features:

        out = str(feature.geometry)
        geom = GEOSGeometry(out)

        if isinstance(geom, Point):
            geom = Point(geom[0], geom[1])

        create_feature(geom, layer=layer, properties=feature.properties)

def import_shapefile(path, layer_uid=None, Token=None):
    try:
        layer = get_layer(layer_uid)
    except:
        raise Exception('Invalid layer UID')

    try:
        new_dir, filename = unzip_from(path)
    except:
        raise Exception('Unable to extract Shapefile')

    location = '/home/dotproj/djangostack-1.7.8-0/apps/django/django_projects/pipelion/data/input/extracted'
    # location = location + '/' + new_dir + '/' + filename
    location = location + '/' + new_dir

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

    print sf.fields

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

        properties = to_json(properties)

        print 'creating feature... {0}'.format(geom.geom_type)
        print 'props: ' + json.dumps(properties)
        create_feature(geom, layer=layer, properties=properties)

import sys
# from osgeo import osr

# def esriprj2standards(shapeprj_path):
#     prj_file = open(shapeprj_path, 'r')
#     prj_txt = prj_file.read()
#     srs = osr.SpatialReference()
#     srs.ImportFromESRI([prj_txt])
#     print 'Shape prj is: %s' % prj_txt
#     print 'WKT is: %s' % srs.ExportToWkt()
#     print 'Proj4 is: %s' % srs.ExportToProj4()
#     srs.AutoIdentifyEPSG()
#     print 'EPSG is: %s' % srs.GetAuthorityCode(None)

def get_apitoken(key):
    ApiToken.objects.get()

def geojson_to_rapid_features(file):
    pass


def shapefile_to_rapid_features(file):
    pass
