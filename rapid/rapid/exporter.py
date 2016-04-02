import itertools
import shapefile
import json
import time

from rapid import models
from rapid.helpers import dir_zip
from rapid.models import DataLayer, Role, GeoView
from rapid.select import DataOperator


class Exporter(object):
    def __init__(self, token_key=None):
        self.token_key = token_key

    # exports a layer to a shapefile (in a default location)
    def export_layer(self, layer_uid, format=None, start=None, end=None):

        data = DataOperator(self.token_key)
        if not data.has_layer_permissions(layer_uid, Role.VIEWER):
            return False

        layer = DataLayer.objects.get(uid=layer_uid)
        all_features = layer.feature_set.all()

        features = all_features

        if start or end:
            if end:
                features = features.filter(create_timestamp__lte=end)
            if start:
                features = features.filter(create_timestamp__gte=start)

        self.export_shapefile(features)
        return True

    # exports a layer to a shapefile (in a default location)
    # iterates through all the associated layers with viewing permissions for user
    def export_geoview(self, geoview_uid, format=None, start=None, end=None):
        geoview = GeoView.objects.get(uid=geoview_uid)
        self.export_shapefile(geoview.get_features(self.token_key))

    # determines feature set's shapefile geometry type
    def get_type(self, features):
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

    # exports a shapefile set with a prj file to the specified location with the included shapefile writer from pyshp
    def write_shapefile(self, sf_writer, output_path, type_str):
        prj_content = 'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],'+\
                      'AUTHORITY["EPSG","6326"]],' +\
                      'PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.01745329251994328,AUTHORITY["EPSG","9122"]],'+\
                      'AUTHORITY["EPSG","4326"]]'

        new_dir = output_path.split('/')[-1] + '_' + type_str
        output_dir = output_path + '/' + new_dir
        sf_writer.save(output_dir + '/' + new_dir)

        prj_file = open(output_dir + '/' + new_dir + '.prj', 'w')
        prj_file.write(prj_content)
        prj_file.close()

        dir_zip(output_dir, 'data/exported/' + new_dir)

    def populate_sf_fields(self, sf, features):
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
        return fields


    def write_sf_feature(self, sf, fields, feature, sf_type):
        if feature.geom.geom_type.lower() == 'Point'.lower():
            sf.point(float(feature.geom.coords[0]), float(feature.geom.coords[1]))
        else:
            parts = self.iterate(feature.geom.coords)

            if sf_type == 3:
                parts = [parts]

            sf.poly(parts=parts, shapeType=sf_type)
        feature_props = json.loads(feature.properties)
        for key in feature_props.keys():
            val = feature_props[key]
            del feature_props[key]
            feature_props[key.encode('utf-8')[:10]] = val
        record_values = []
        for field in fields:
            key = field['name']

            if key in feature_props:
                record_values.append(feature_props[key])
            else:
                record_values.append(None)
        sf.record(*record_values)

    def iterate(self, t):
        return [self.iterate(i) for i in t] if isinstance(t, (list, tuple)) else t

    def write_geom_type_sf(self, output_path, geom_type_group):
        features = list(geom_type_group[1])
        sf_type, type_str = self.get_type(features)
        sf = shapefile.Writer(sf_type)
        sf.autobalance = 1
        fields = self.populate_sf_fields(sf, features)
        for feature in features:
            self.write_sf_feature(sf, fields, feature, sf_type)
        self.write_shapefile(sf, output_path, type_str)

    # writes a layer to a shapefile
    def write_layer_sf(self, layer_group):
        output_path = 'data/temp/'
        data = DataOperator(self.token_key)
        directory = data.get_layer(layer_group[0]).descriptor
        output_path += directory
        geom_type_groups = itertools.groupby(sorted(list(layer_group[1]), key=lambda abc: abc.geom.geom_typeid),
                                             lambda y: y.geom.geom_typeid)
        for geom_type_group in geom_type_groups:
            self.write_geom_type_sf(output_path, geom_type_group)

    # aggregates (like GROUP BY) features by their layer
    def group_features_by_layer(self, features):
        layer_groups = itertools.groupby(sorted(list(features), key=lambda z: z.layer_id), lambda x: x.layer_id)
        return layer_groups

    # exports collection of features to a shapefile in the default location
    def export_shapefile(self, features):
        layer_groups = self.group_features_by_layer(features)

        for layer_group in layer_groups:
            self.write_layer_sf(layer_group)