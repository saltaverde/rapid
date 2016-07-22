import xml.etree.ElementTree as et
from rapid.settings import FEATURETYPE_XML_TEMPLATE_PATH, GEOSERVER_REST_ENDPOINT, TEMP_DATA_DIR, GEOSERVER_ADMIN_USER, GEOSERVER_ADMIN_PASSWORD
from rapid.models import *
from geoserver.catalog import Catalog
import requests
import os

class Geoserver():
    def __init__(self):
        self.restEndpoint = GEOSERVER_REST_ENDPOINT

    def createFeatureTypeFromQuerySet(self, descriptor, queryset):

        cat = Catalog(GEOSERVER_REST_ENDPOINT)
        lyrs = cat.get_layers()
        lyr_names = [lyr.name for lyr in lyrs]

        # Check for duplicate layer names and append a count number for disambiguation
        count = 2
        lyr_name = descriptor.replace(' ', '_').lower()
        if lyr_name in lyr_names:
            lyr_name = lyr_name + '_' + str(count)

        while lyr_name in lyr_names:
            count += 1
            lyr_name = lyr_name.replace('_' + str(count), '_' + str(count + 1))

        # To be continued . . .

    def createFeatureTypeFromUid(self, uid):
        """
        Returns an XML formatted string used to post to the Geoserver REST API
        """
        try:
            layer_state = DataLayer.objects.get(uid=uid).__getstate__()
        except:
            return None

        if layer_state is not None:
            # Methods from gsconfig lib
            cat = Catalog(GEOSERVER_REST_ENDPOINT)
            # lyrs = cat.get_layers()
            # lyr_names = [lyr.name for lyr in lyrs]

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

            # Check for duplicate layer names and append a count number for disambiguation
            '''
            count = 2
            lyr_name = layer_state['descriptor'].replace(' ', '_').lower()
            if lyr_name in lyr_names:
                lyr_name = lyr_name + '_' + str(count)

            while lyr_name in lyr_names:
                count += 1
                lyr_name = lyr_name.replace('_' + str(count), '_' + str(count + 1))
            '''

            # Set appropriate values in the xml tree
            title.text = layer_state['descriptor']
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

            geomType.text = layer_state['geom_type']

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