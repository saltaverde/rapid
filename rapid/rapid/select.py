import fnmatch
import geojson
import os
import shapefile
import shortuuid
import urllib2
from rapid import models
from rapid.helpers import *
from rapid.models import GeoView, DataLayer, Feature, ApiToken, DataLayerRole, Role, GeoViewRole
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import Point
import json

class DataOperator(object):
    def __init__(self, token_key=None):
        self.token_key = token_key

    def get_apitoken(self):
        try:
            return ApiToken.objects.get(key=self.token_key)
        except:
            return None

    def has_layer_permissions(self, layer_uid, role):
        try:
            layer = DataLayer.objects.get(uid=layer_uid)
        except:
            return False

        if layer.is_public and role == Role.VIEWER:
            return True

        if not self.token_key:
            return False

        owners = DataLayerRole.objects.filter(token__key=self.token_key, layer__uid=layer_uid, role=Role.OWNER)
        editors = DataLayerRole.objects.filter(token__key=self.token_key, layer__uid=layer_uid, role=Role.EDITOR)
        viewers = DataLayerRole.objects.filter(token__key=self.token_key, layer__uid=layer_uid, role=Role.VIEWER)

        if role == Role.OWNER:
            if owners.count() > 0:
                return True
        elif role == Role.EDITOR:
            if owners.count() > 0 or editors.count() > 0:
                return True
        elif role == Role.VIEWER:
            if owners.count() > 0 or editors.count() > 0 or viewers.count() > 0:
                return True

        return False

    def has_geoview_permissions(self, geoview_uid, role):
        try:
            geoview = GeoView.objects.get(uid=geoview_uid)
        except:
            return False

        if geoview.is_public and role == Role.VIEWER:
            return True

        if not self.token_key:
            return False

        owners = GeoViewRole.objects.filter(token__key=self.token_key, geo_view__uid=geoview_uid, role=Role.OWNER)
        editors = GeoViewRole.objects.filter(token__key=self.token_key, geo_view__uid=geoview_uid, role=Role.EDITOR)
        viewers = GeoViewRole.objects.filter(token__key=self.token_key, geo_view__uid=geoview_uid, role=Role.VIEWER)

        if role == Role.OWNER:
            if owners.count() > 0:
                return True
        elif role == Role.EDITOR:
            if owners.count() > 0 or editors.count() > 0:
                return True
        elif role == Role.VIEWER:
            if owners.count() > 0 or editors.count() > 0 or viewers.count() > 0:
                return True

        return False

    def get_apitokens(self):
        return [{"uid": x.uid, "descriptor": x.descriptor} for x in ApiToken.objects.all()]

    def get_feature(self, uid):
        try:
            feature = Feature.objects.get(uid=uid)
        except:
            return None

        return feature

    def create_feature(self, geom, layer=None, properties=None):

        if not type(layer) is models.DataLayer and type(layer) is str:
            layer = self.get_layer(layer)

        feature = Feature(layer=layer, geom=geom)
        feature.uid = get_uid()
        if properties:
            feature.properties = properties
        feature.save()
        return feature.uid

    def update_feature(self, uid, geom, layer=None, archive=None, properties=None):
        feature = self.get_feature(uid)
        feature.geom = geom
        feature.layer = layer
        if properties:
            feature.properties = properties
        feature.archive = archive
        feature.save()
        return feature.uid

    def delete_feature(self, uid):
        try:
            Feature.objects.get(uid=uid).delete()
            return True
        except:
            return False

    def create_layer(self, descriptor, is_public, properties):
        layer = DataLayer(descriptor=descriptor, properties=properties, is_public=is_public)
        layer.uid = get_uid()
        layer.save()
        role = DataLayerRole(layer_id=layer.uid, token_id=self.get_apitoken().uid, role=Role.OWNER)
        role.save()
        return layer.uid

    def get_layers(self):
        return [lyr for lyr in DataLayer.objects.all() if self.has_layer_permissions(lyr.uid, Role.VIEWER)]

    def get_layer(self, uid):
        layer = DataLayer.objects.filter(uid=uid)
        return layer[0]

    def get_layer_features(self, uid, start=None, stop=None):
        layer = self.get_layer(uid)
        if start and stop:
            features = layer.feature_set.filter(create_timestamp__lte=start, create_timestamp__gte=stop)
        elif start:
            features = layer.feature_set.filter(create_timestamp__lte=start)
        elif stop:
            features = layer.feature_set.filter(create_timestamp__gte=stop)
        else:
            features = layer.feature_set.all()

        return features

    def delete_layer(self, uid):
        try:
            for feature in DataLayer.objects.get(uid=uid):
                Feature.objects.get(uid=feature.uid).delete()
            DataLayer.objects.get(uid=uid).delete()
            return True
        except:
            return False

    def get_geoviews(self):
        return list(GeoView.objects.all())

    def get_geoview(self, uid, file=False):
        if not file:
            geoview = GeoView.objects.filter(uid=uid)[0]
            return geoview
        else:
            return "somefile.geojson"

    def delete_geoview(self, uid):
        try:
            GeoView.objects.get(uid=uid).delete()
            return True
        except:
            return False

    def create_geoview(self, geom, descriptor, properties, public=False):
        view = GeoView(geom=geom, descriptor=descriptor, properties=properties, is_public=public)
        view.uid = get_uid()
        view.save()

        role = GeoViewRole(geo_view=view, token_id=self.get_apitoken().uid, role=Role.OWNER)
        role.save()
        return view.uid

    def add_layer_to_geoview(self, geoview_uid, layer_uid):
        geoview = GeoView.objects.filter(uid=geoview_uid)
        layer = DataLayer.objects.filter(uid=layer_uid)

        if geoview.count() > 0 and layer.count() > 0:
            geoview[0].add_layer(layer[0])
            geoview[0].save()
            return "SUCCESS: ", geoview[0].uid, " + ", layer[0].uid
        return "FAILURE: incorrect uid"


    def remove_layer_from_geoview(self, geoview_uid, layer_uid):
        geoview = GeoView.objects.filter(uid=geoview_uid)
        layer = DataLayer.objects.filter(uid=layer_uid)

        if geoview.count() > 0 and layer.count() > 0:
            geoview[0].remove_layer(layer[0])
            geoview[0].save()
            return "SUCCESS: ", geoview[0].uid, " + ", layer[0].uid
        return "FAILURE: incorrect uid"
