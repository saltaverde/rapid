from django.contrib.admin import helpers
import jsonpickle
import itertools
import shapefile
import time
from rapid import models
from rapid.database.select import get_layer
from rapid.helpers import dir_zip
import json


def export_layer(layer, format, start=None, end=None):
    # if layer not found, error
    # if start > end, error
    # etc.

    if format == models.FileType.GEOJSON:
        # return geojson
        pass
    elif format == models.FileType.SHAPEFILE:
        # return shapefile
        pass
    else:
        # error or use default
        pass

def export_geoview(geoview, type, start=None, end=None):
    # and so on
    pass


def get_type(features):
    type_str = features[0].geom.geom_type
    sf_type = None
    if type_str.lower() == 'MultiPolygon'.lower():
        sf_type = shapefile.POLYGONM
    elif type_str.lower() == 'MultiLineString'.lower():
        sf_type = shapefile.POLYLINEM
    elif type_str.lower() == 'MultiPoint'.lower():
        sf_type = shapefile.MULTIPOINT
    elif type_str.lower() == 'Polygon'.lower():
        sf_type = shapefile.POLYGON
    elif type_str.lower() == 'LinearRing'.lower():
        sf_type = shapefile.POLYLINE
    elif type_str.lower() == 'LineString'.lower():
        sf_type = shapefile.POLYLINE
    elif type_str.lower() == 'Point'.lower():
        sf_type = shapefile.POINT
    return sf_type, type_str


def export_shapefile(features_queryset):
    prj_content = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4326"]]'

    layer_groups = itertools.groupby(sorted(list(features_queryset), key=lambda z: z.layer_id), lambda x: x.layer_id)
    for layer_group in layer_groups:
        output_path = 'data/output/'
        directory = get_layer(layer_group[0]).descriptor
        output_path += directory
        print output_path

        geom_type_groups = itertools.groupby(sorted(list(layer_group[1]), key=lambda abc: abc.geom.geom_typeid), lambda y: y.geom.geom_typeid)
        for geom_type_group in geom_type_groups:

            features = list(geom_type_group[1])
            sf_type, type_str = get_type(features)

            sf = shapefile.Writer(sf_type)
            sf.autobalance = 1

            all_properties = {}
            for feature in features:
                prop_dict = json.loads(feature.properties)
                for key in prop_dict.keys():
                    all_properties.setdefault(key, []).append(prop_dict[key])

            fields = []
            for key in all_properties.keys():
                name = key[:10]
                field_type = None
                length = None
                deci = 0

                for item in all_properties[key]:
                    if type(item) is int:
                        field_type = 'N'
                        length = 10
                        break
                    if type(item) is float:
                        field_type = 'N'
                        length = 10
                        # deci = 10
                        break
                    if type(item) is long:
                        field_type = 'L'
                        length = 10
                        break
                    else:
                        field_type = 'C'
                        length = 64
                        break

                fields.append({"name": name.encode('utf-8'), "type": field_type, "length": length, "deci": deci})

            for field in fields:
                sf.field(name=field['name'], fieldType=field['type'], size=field['length'], decimal=field['deci'])

            print 'Own fields:'
            print fields
            print 'sf fields:'
            print sf.fields

            print 'LEN'
            print len(sf.fields)

            for feature in features:
                print 'Exporting feature...'
                print feature.geom.geom_type
                print feature.geom.coords

                if feature.geom.geom_type.lower() == 'Point'.lower():
                    sf.point(float(feature.geom.coords[0]), float(feature.geom.coords[1]))
                else:
                    sf.poly(parts=feature.geom.coords, shapeType=sf_type)

                feature_props = json.loads(feature.properties)
                print 'Unmodified props'
                print feature_props

                for key in feature_props.keys():
                    val = feature_props[key]
                    del feature_props[key]
                    feature_props[key.encode('utf-8')[:10]] = val

                print 'Changed props'
                print feature_props
                print len(feature_props.keys())

                record_values = []
                for field in fields:
                    key = field['name']

                    if key in feature_props:
                        record_values.append(feature_props[key])
                    else:
                        record_values.append(None)

                print 'LEN'
                print len(sf.fields)
                sf.record(*record_values)

            print 'LEN2'
            print len(sf.shapes())
            print len(sf.records)


            sf.save(output_path + '_' + type_str)

        # dir_zip(output_path)
    # dir_zip(output_path)