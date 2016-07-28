import xml.etree.ElementTree as et
from rapid.settings import FEATURETYPE_XML_TEMPLATE_PATH, GEOSERVER_REST_ENDPOINT, TEMP_DATA_DIR, GEOSERVER_ADMIN_USER, GEOSERVER_ADMIN_PASSWORD, GEOFENCE_RULES_URL
from rapid.geofence import getGeofenceRules, removeGeofenceRule, addGeofenceRule
from rapid.models import *
from geoserver.catalog import Catalog
import xml.etree.ElementTree as ET
import requests
import os

class Geoserver():
    def __init__(self):
        self.restEndpoint = GEOSERVER_REST_ENDPOINT

    #def createFeatureTypeFromQuerySet(self, descriptor, queryset):
    # To be continued . . .

    def synchronizeLayers(self):
        '''
        Synchronizes layers/rules in the postgresql database, Geoserver, and Geofence. All three will match postgresql database.
        '''

        to_return = True

        permanent_gs_layers = ['rapid_geoview_layers','rapid_feature','rapid_geoview']
        rapid_layers = {lyr.uid for lyr in DataLayer.objects.all() if lyr.feature_set.count() > 0}

        cat = Catalog(GEOSERVER_REST_ENDPOINT)
        store = cat.get_store('RapidData')
        gs_layers = {lyr.name for lyr in store.get_resources() if lyr.name not in permanent_gs_layers}

        gf_rules_ids = {(rule.find('layer').text, int(rule.find('id').text)) for rule in ET.fromstring(getGeofenceRules('admin').content)[:-1]}
        gf_rules = {rule[0] for rule in gf_rules_ids}

        gs_layers_to_remove = gs_layers.difference(rapid_layers)
        gs_layers_to_add = rapid_layers.difference(gs_layers)

        gf_rules_to_remove = gf_rules.difference(rapid_layers)
        gf_rules_to_add = rapid_layers.difference(gf_rules)

        if len(gs_layers_to_add) == 0 and len(gs_layers_to_remove) == 0:
            if len(gf_rules_to_add) == 0 and len(gf_rules_to_remove) == 0:
                return to_return

        elif len(gs_layers_to_remove) > 0:

            for lyr_uid in gs_layers_to_remove:
                print "Removing Geoserver layer {0}. . .".format(lyr_uid)
                response = self.removeFeatureType(lyr_uid)
                if response.status_code == 200:
                    print "Success!"
                else:
                    print "Failed to remove layer {0}".format(lyr_uid)
                    to_return = False
                    print response.content

        elif len(gs_layers_to_add) > 0:

            for uid in gs_layers_to_add:
                print "Adding FeatureType to Geoserver: {0}".format(uid)
                xml = self.createFeatureTypeFromUid(uid)
                response = self.sendFeatureType(xml)
                if response.status_code == 200:
                    print "Success!"
                else:
                    print "Failed to add FeatureType {0}".format(uid)
                    to_return = False
                    print response.content

        if len(gf_rules_to_add) == 0 and len(gf_rules_to_remove) == 0:
                return to_return

        elif len(gf_rules_to_remove) > 0:

            gf_ids_to_remove = [rule for rule in gf_rules_ids if rule[0] in gf_rules_to_remove]

            for rule in gf_ids_to_remove:
                print "Removing Geofence rule for layer {0}".format(rule[0])
                response = removeGeofenceRule(rule[1])
                if response.status_code == 200:
                    print "Success!"
                else:
                    print "Failed to remove layer {0}".format(lyr_uid)
                    to_return = false
                    print response.content

        elif len(gf_rules_to_add) > 0:
            for rule in gf_rules_to_add:
                response = addGeofenceRule(layer=rule)
                if response.status_code == 200:
                    print "Success!"
                else:
                    print "Failed to add Geofence rule for layer {0}".format(rule)
                    to_return = False
                    print response.content

        return to_return

    def removeFeatureType(self, uid):
        url = os.path.join(GEOSERVER_REST_ENDPOINT, '/workspaces/rapid/datastores/RapidData/featuretypes', uid)
        return requests.delete(url)

    def createFeatureTypeFromUid(self, uid):
        """
        Returns an XML formatted string used to post to the Geoserver REST API
        """
        try:
            layer = DataLayer.objects.get(uid=uid)
        except:
            return None

        if layer is not None:
            # No ability to create featuretypes backed by a DB in gsconfig as of now
            # Homemade solution for injecting values into xml parsed from a template
            tree = et.parse(FEATURETYPE_XML_TEMPLATE_PATH)
            featureType = tree.getroot()

            metadata = featureType.find('metadata')
            name = featureType.find('name')
            nativeName = featureType.find('nativeName')
            title = featureType.find('title')

            tableName = metadata.find('entry').find('virtualTable').find('name')
            sqlView = metadata.find('entry').find('virtualTable').find('sql')
            geomType = metadata.find('entry').find('virtualTable').find('geometry').find('type')
            sridElem = metadata.find('entry').find('virtualTable').find('geometry').find('srid')

            # Set appropriate values in the xml tree
            title.text = layer.descriptor
            tableName.text = uid
            sridElem.text = '4326'

            if name is not None:
                name.text = tableName.text
            else:
                name.text = 'Not provided'

            if nativeName is not None:
                nativeName.text = name.text
            else:
                nativeName.text = 'Not provided'

            geomType.text = layer.feature_set.first().geom.geom_type

            if sqlView is not None:
                sqlView.text = "select * from rapid_feature where layer_id='" + uid + "'"

            return et.tostring(featureType)

        else:
            return None

    def sendFeatureType(self, xml):
        # TODO: Change Geoserver auth based on the user initiating the featuretype creation
        auth = (GEOSERVER_ADMIN_USER, GEOSERVER_ADMIN_PASSWORD)
        url = os.path.join(GEOSERVER_REST_ENDPOINT, 'workspaces/rapid', 'datastores/RapidData', 'featuretypes')
        headers = {'Content-Type':'application/xml'}
        response = requests.post(url, auth=auth, data=xml, headers=headers)

        return response