from django.contrib.gis.db import models
from django_enumfield import enum
from django.contrib.auth.models import User
#from django.contrib.postgres.fields import JSONField

import hmac
import json
import os
import shortuuid
import uuid
import datetime
from rapid.helpers import get_uid


class Role(enum.Enum):
    VIEWER = 0
    EDITOR = 1
    OWNER = 2

    labels = {
        VIEWER: 'Viewer',
        EDITOR: 'Editor',
        OWNER: 'Owner'
    }


class FileType(enum.Enum):
    GEOJSON = 0
    SHAPEFILE = 1

    labels = {
        GEOJSON: 'GeoJSON',
        SHAPEFILE: 'Shapefile'
    }

class GeoView(models.Model):
    uid = models.TextField(primary_key=True)
    descriptor = models.TextField()
    geom = models.GeometryField(null=True)
    bbox = models.PolygonField(null=True)
    properties = models.TextField(null=True)
    layers = models.ManyToManyField('DataLayer')
    is_public = models.BooleanField(default=False)

    # unpublished flags. workaround for including/excluding extra info in output
    include_layers = models.NullBooleanField(null=True)
    include_geom = models.NullBooleanField(null=True)
    token_key = models.TextField(null=True)

    objects = models.GeoManager()

    def __str__(self):
        return "GeoView { id: " + str(self.uid) + ", descriptor: " + self.descriptor + " }"

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop('layers', None)
        state['geom'] = {'type': self.geom.geom_type, 'coordinates': self.geom.coords}
        # state['layers'] = self.get_json_features()
        if self.include_layers:
            # state['layers'] = list(self.layers.all().values_list('uid', flat=True))
            state['layers'] = self.get_json_features()

        if not self.include_geom:
            del state['geom']

        del state['_state']
        del state['token_key']
        del state['include_layers']
        del state['include_geom']
        return state

    def add_layer(self, layer):
        # error checking here

        self.layers.add(layer)

    def get_json_features(self):
        results = []
        for layer in self.layers.all():
            features = layer.feature_set.filter(geom__intersects=self.geom)
            # results.append({'uid': layer.uid, 'descriptor': layer.descriptor,
            #                 'features': list(features.values_list('uid', flat=True))})
            if layer.has_permissions(self.token_key, Role.VIEWER):
                features = layer.feature_set.filter(geom__intersects=self.geom)
                results.append({'uid': layer.uid, 'descriptor': layer.descriptor, 'features': list(features.values_list('uid', flat=True))})

        return results

    def get_features(self, token_key):
        results = []
        for layer in self.layers.all():
            if layer.has_permissions(token_key, Role.VIEWER):
                print 'Exporting {0} features in {1}'.format(len(layer.feature_set.all()), layer.descriptor)
                features = layer.feature_set.filter(geom__intersects=self.geom)
                results.extend(list(features))

        return results


    def remove_layer(self, layer):
        # error checking here

        self.layers.remove(layer)


class DataLayer(models.Model):
    uid = models.TextField(primary_key=True)
    descriptor = models.TextField()
    properties = models.TextField(null=True)
    is_public = models.BooleanField(default=False)
    srid = models.TextField(null=True)

    # unpublished flag. workaround for including/excluding extra info in output
    include_features = models.BooleanField(default=True)

    objects = models.GeoManager()

    def __getstate__(self):
        state = self.__dict__.copy()
        state['uid'] = self.uid

        if self.feature_set.count() > 0:
            state['geom_type'] = self.feature_set.all()[0].geom.geom_type
        else:
            state['geom_type'] = None

        if self.include_features:
            state['features'] = list(self.feature_set.all().values_list('uid', flat=True))
            #need to add "include_range" to check for start and stop filter of features
        else:
            state['features'] = None

        state['srid'] = self.srid

        del state['_state']

        return state

    def has_permissions(self, token_key, role):
        if self.is_public and role == Role.VIEWER:
            return True

        if not token_key:
            return False

        owners = DataLayerRole.objects.filter(token__key=token_key, layer__uid=self.uid, role=Role.OWNER)
        editors = DataLayerRole.objects.filter(token__key=token_key, layer__uid=self.uid, role=Role.EDITOR)
        viewers = DataLayerRole.objects.filter(token__key=token_key, layer__uid=self.uid, role=Role.VIEWER)

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


class DataSource(models.Model):
    url = models.TextField(null=True)
    layer = models.ForeignKey('DataLayer', null=True)
    update_interval = models.TimeField(null=True)
    expected_type = models.TextField(null=True)  # internet media type
    properties = models.TextField(null=True)


class Feature(models.Model):
    uid = models.TextField(primary_key=True)
    geom = models.GeometryField(null=True)
    bbox = models.PolygonField(null=True)
    #properties = JSONField()
    properties = models.TextField(null=True)
    create_timestamp = models.TimeField(auto_now_add=True, null=True, db_index=True)
    layer = models.ForeignKey(DataLayer, null=True)
    hash = models.TextField(null=True, unique=True, db_index=True)
    modified_timestamp = models.TimeField(auto_now=True, null=True)

    objects = models.GeoManager()

    def __str__(self):
        return 'uid {0}, time {1}'.format(self.uid, self.create_timestamp)

    def getGeoJson(self):
        if self.geom:
            return self.geom.geojson
        else:
            return ""

    def __getstate__(self):
        state = self.__dict__.copy()
        state['geometry'] = {'type': self.geom.geom_type, 'coordinates': self.geom.coords}
        state['type'] = 'Feature'
        state['properties'] = json.loads(self.properties)
        del state['_state']
        del state['geom']
        return state


class ApiToken(models.Model):
    uid = models.TextField(primary_key=True)
    key = models.TextField(unique=True, db_index=True)
    descriptor = models.TextField(unique=True)
    issued = models.TimeField(null=True, auto_now_add=True)

    def setup(self, descriptor):
        self.uid = get_uid()
        self.key = self.generate_secure_key()
        self.descriptor = descriptor
        self.issued = datetime.datetime.now()

    @staticmethod
    def generate_secure_key():
        try:
            from hashlib import sha1
        except ImportError:
            import sha
            sha1 = sha.sha

        # UUID generated from 16 bytes of randomness from /dev/urandom
        new_uuid = uuid.uuid4()
        friendly_digest = hmac.new(str(new_uuid), digestmod=sha1).hexdigest()
        return friendly_digest

    def __str__(self):
        return self.uid + ', ' + self.descriptor

class GeoViewRole(models.Model):
    token = models.ForeignKey(ApiToken)
    role = enum.EnumField(Role, default=Role.OWNER)
    geo_view = models.ForeignKey(GeoView)
    objects = models.GeoManager()

class DataLayerRole(models.Model):
    token = models.ForeignKey(ApiToken)
    role = enum.EnumField(Role)
    layer = models.ForeignKey(DataLayer)
    objects = models.GeoManager()

class GeoFile(models.Model):
    uid = models.TextField(primary_key=True)
    content = models.BinaryField(null=True)
    filename = models.TextField(null=True)
    geom = models.GeometryField(null=True)
    descriptor = models.TextField(null=True)
    objects = models.GeoManager()

    @staticmethod
    def create_and_save_from_file(path, geom, descriptor=None):
        filename = os.path.basename(path)
        file = open(path, mode='r')

        geofile = GeoFile()
        geofile.uid = get_uid()
        geofile.filename = filename
        geofile.content = file.read()
        geofile.geom = geom
        geofile.descriptor = descriptor

        geofile.save()
        file.close()
        return geofile

    def write_to_disk_from_db(self, filepath):
        file = open(filepath, 'w')
        file.write(self.content)
        file.close()

    @staticmethod
    def get_geofiles_in_geom(geom):
        return GeoFile.objects.filter(geom__intersects=geom)

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    token = models.ForeignKey(ApiToken)