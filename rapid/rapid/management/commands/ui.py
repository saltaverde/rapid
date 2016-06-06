from django.core.management import BaseCommand
import time
from datetime import timedelta

from rapid.exporter import Exporter
from rapid.select import *
from rapid.helpers import *
from rapid.models import *
from rapid.importer import *
from rapid.views import create_featuretype
from rapid.geofence import *

class Command(BaseCommand):

    def get_token(self):
        token = None
        done = False
        while not done:
            response = raw_input('Enter your private API key (\'d\' for default account,\'q\' to quit): ')
            response = response.strip()
            print ''

            if response.lower() == 'q':
                token = None
                done = True
            elif response.lower() == 'd':
                try:
                    token = ApiToken.objects.get(descriptor='Default')
                except:
                    token = ApiToken()
                    token.setup('Default')
                    token.save()
                print 'API token active: {0}'.format(token.descriptor)
                done = True
            else:
                try:
                    token = ApiToken.objects.get(key=response)
                    print 'API token active: {0}'.format(token.descriptor)
                    done = True
                except:
                    print 'This key was not found. You may need to first create an API token.'
        token = token
        return token

    def print_tokens(self, base_endpoint):
        r = requests.get(base_endpoint + '/tokens')
        print 'Fetched URL: {0}'.format(r.url)
        print 'API Tokens:'
        for each in r.json():
            print '  {0} - UID: {1} - Key: Private'.format(each['descriptor'], each['uid'])

    def handle_geoview_option(self, base_endpoint, geoview_uid, r, response, response_num, token_key, token_params):
        print ''
        if response == '1':
            print 'Add/remove GeoView Permissions'
            menu_options = [
                '  1 - Owner',
                '  2 - Editor',
                '  3 - Viewer',
            ]
            for each in menu_options:
                print each

            role = None
            while not role:
                response = raw_input('Select a menu option (or \'q\' to go back): ').strip()
                print ''
                if response == '1':
                    role = 'owner'
                elif response == '2':
                    role = 'editor'
                elif response == '3':
                    role = 'viewer'
                elif response == 'q':
                    return
                else:
                    print 'Invalid option.'

            option = None
            while not option:
                response = raw_input('Add or remove {0} (\'a\' or \'r\'): '.format(role)).strip()
                print ''
                if response.lower() == 'a':
                    option = 'add'
                elif response.lower() == 'r':
                    option = 'remove'
                else:
                    print 'Invalid option.'

            r = requests.get(base_endpoint + '/tokens')
            print 'API Tokens:'
            for each in r.json():
                print '  {0} - UID: {1}'.format(each['descriptor'], each['uid'])

            token_uid = None

            while not token_uid:
                response = raw_input('Enter the access token\'s UID: ').strip()
                print ''
                if len(response) > 0:
                    token_uid = response

            for each in r.json():
                if each['uid'] == token_uid:
                    des = each['descriptor']

            confirm = None
            while not confirm:
                response = raw_input(
                    'Confirm (\'y\' or \'n\'): {0} token \'{1}\' as {2}? '.format(option, des, role))
                print ''
                if response.lower() == 'y':
                    print 'running'
                    confirm = True
                    r = requests.get(
                        base_endpoint + '/geoview/{0}/{1}/{2}/{3}'.format(geoview_uid, option, role, token_uid),
                        params=token_params)
                    print 'Called endpoint: {0}'.format(r.url)
                    # print r.text
                elif response.lower() == 'n':
                    print 'Canceled.'
                    confirm = True
                else:
                    print 'Invalid option.'

            pass
        elif response == '2':

            r = requests.get(base_endpoint + '/geoview/{0}'.format(geoview_uid), params=token_params)

            print 'Accessed endpoint: {0}'.format(r.url)
            print 'Layers in GeoView:'

            layers = r.json()['layers']
            for i in xrange(len(layers)):
                print '  {0} - {1}'.format(i, layers[i]['descriptor'])

            if len(layers) == 0:
                print '  [No layers]'

            response = raw_input(
                'Select which layer to remove, or enter \'a\' to add a layer (or \'q\' to go back): ').strip()

            option = None
            while not option:
                if response.lower() == 'a':
                    all_layers = None
                    r = requests.get(base_endpoint + '/layer/', params=token_params)
                    all_layers = r.json()
                    for i in xrange(len(all_layers)):
                        print '  {0} - {1}'.format(i, all_layers[i]['descriptor'])

                    response = raw_input(
                        'Select a layer to add (or \'q\' to go back): ').strip()

                    if response.isdigit():
                        layer = all_layers[int(response)]
                        r = requests.get(
                            base_endpoint + '/geoview/{0}/add/layer/{1}'.format(geoview_uid, layer['uid']),
                            params=token_params)
                        print 'Accessed endpoint: {0}'.format(r.url)
                        print 'Added layer to GeoView'
                        # return
                    elif response.lower() == 'q':
                        return


                elif response.lower() == 'q':
                    return
                elif response.isdigit():
                    choice = int(response)
                    layer = layers[choice]
                    r = requests.get(
                        base_endpoint + '/geoview/{0}/remove/layer/{1}'.format(geoview_uid, layer['uid']),
                        params=token_params)
                    print 'Accessed endpoint: {0}'.format(r.url)
                    print r.text
                    print r.json()['status']
                    print 'Removed layer from GeoView'
        elif response == '3':
            json_entry = r.json()[response_num]
            geoview_uid = json_entry['uid']

            print 'Exporting...'
            Exporter(token_key).export_geoview(geoview_uid, end=None)
            print 'Done.'
            # return
        elif response == '4':
            r = requests.delete('{0}/geoview/{1}'.format(base_endpoint, geoview_uid), params=token_params)
            print r.json()

    def select_geoview(self, base_endpoint, count, response_num, r, token_key, token_params):
        if response_num == count:
            print 'Creating a GeoView:'

            response = raw_input('Save the polygon of interest into geoview.geojson then press ENTER (or \'q\' to go back): ').strip()
            if response == 'q':
                return

            geom = open('data/geoview.geojson', 'r').read().strip()

            des = raw_input('Enter a descriptor: ')
            public = raw_input('Is this a public GeoView (\'y\' or \'n\')? ')

            if public.lower() == 'y':
                public = True
            else:
                public = False

            r = requests.post(base_endpoint + '/geoview/', params=token_params,
                              data=json.dumps({"geom": geom, "des": des, "public": public}))
        elif 0 <= response_num < count:
            json_entry = r.json()[response_num]
            geoview_uid = json_entry['uid']

            print 'GeoView: {0}\nUID: {1}'.format(json_entry['descriptor'], geoview_uid)

            menu_options = [
                '  1 - Add/remove permissions',
                '  2 - Layers',
                '  3 - Export',
                '  4 - Delete'
            ]
            for each in menu_options:
                print each

            response = raw_input('Select a menu option (or \'q\' to go back): ').strip()
            self.handle_geoview_option(base_endpoint, geoview_uid, r, response, response_num, token_key, token_params)

    def handle_geoview(self, base_endpoint, response, token_key, token_params):
        r = requests.get(base_endpoint + '/geoview', params=token_params)
        print 'Fetched URL: {0}'.format(r.url)
        print 'Select a GeoView or add a GeoView:'
        count = 0
        for i in xrange(len(r.json())):
            des = r.json()[i]['descriptor']
            print '  ' + str(i) + ' - ' + des
            count = i
        count += 1
        print '  ' + str(count) + ' - Create a GeoView'
        response = raw_input('Select a menu option (or \'q\' to go back): ').strip()

        if response == 'q':
            return

        print ''
        try:
            response_num = int(response)
        except:
            print 'Invalid option.'

        self.select_geoview(base_endpoint, count, response_num, r, token_key, token_params)

    def handle_layer_activity(self, base_endpoint, layer, response, token_key, token_params):
        print ''
        if response == '1':
            print 'Add/remove Layer Permissions'
            menu_options = [
                '  1 - Owner',
                '  2 - Editor',
                '  3 - Viewer',
            ]
            for each in menu_options:
                print each

            role = None
            while not role:
                response = raw_input('Select a menu option (or \'q\' to go back): ').strip()
                print ''
                if response == '1':
                    role = 'owner'
                elif response == '2':
                    role = 'editor'
                elif response == '3':
                    role = 'viewer'
                elif response == 'q':
                    return
                else:
                    print 'Invalid option.'

            option = None
            while not option:
                response = raw_input('Add or remove {0} (\'a\' or \'r\'): '.format(role)).strip()
                print ''
                if response.lower() == 'a':
                    option = 'add'
                elif response.lower() == 'r':
                    option = 'remove'
                else:
                    print 'Invalid option.'

            r = requests.get(base_endpoint + '/tokens')
            print 'API Tokens:'
            for each in r.json():
                print '  {0} - UID: {1}'.format(each['descriptor'], each['uid'])

            token_uid = None

            while not token_uid:
                response = raw_input('Enter the access token\'s UID: ').strip()
                print ''
                if len(response) > 0:
                    token_uid = response

            for each in r.json():
                if each['uid'] == token_uid:
                    des = each['descriptor']

            confirm = None
            while not confirm:
                response = raw_input(
                    'Confirm (\'y\' or \'n\'): {0} token \'{1}\' as {2}? '.format(option, des, role))
                print ''
                if response.lower() == 'y':
                    print 'running'
                    confirm = True
                    r = requests.get(
                        base_endpoint + '/layer/{0}/{1}/{2}/{3}'.format(layer['uid'], option, role, token_uid),
                        params=token_params)
                    print 'Called endpoint: {0}'.format(r.url)
                    # print r.text
                elif response.lower() == 'n':
                    print 'Canceled.'
                    confirm = True
                else:
                    print 'Invalid option.'
            pass

        elif response == '2':
            # response = raw_input('Only export recent data from last 7 days (\'y\' or \'n\'): ').strip()
            #
            # if response.lower() == 'y':
            # end = datetime.date.today() - timedelta(days=7)
            # else:
            # end = None

            print 'Exporting...'
            try:
                Exporter(token_key).export_layer(layer['uid'], end=None)
            except Exception, e:
                log_exception(e)
                print 'There was an error during export.'

        elif response == '3':
            r = requests.delete('{0}/layer/{1}'.format(base_endpoint, layer['uid']), params=token_params)
            print r.json()

        elif response == '4':

            for root, dirnames, filenames in os.walk('data/dropbox'):
                files = []
                for filename in fnmatch.filter(filenames, '*.zip'):
                    files.append(os.path.join(root, filename))

                for i in xrange(len(files)):
                    filename = os.path.basename(files[i])
                    filename = os.path.splitext(filename)[0]
                    print '  {0} - {1}'.format(i, filename)

                response = raw_input('Enter a file to import into the layer (or \'q\' to go back): ').strip()

                if response == 'q':
                    return

                if response.isdigit():
                    choice = int(response)

                    data = DataOperator(token_key)

                    role = DataLayerRole(layer_id=layer.uid, token=data.get_apitoken(), role=Role.OWNER)
                    role.save()

                    importer = Importer(token_key)
                    print 'Importing...'
                    importer.import_shapefile(files[choice], layer['uid'])

                    # Add featuretype to Geoserver
                    lyr_name = create_featuretype(layer['uid'])
                    if lyr_name is None:
                        print 'WARNING: featureType {0} was not successfully sent to Geoserver'.format(layer_uid)
                        return

                    if layer['is_public'] == True:
                        addGeofenceRule('*', lyr_name)
                    else:
                        username = ApiToken.objects.get(key=token_key).descriptor
                        addGeofenceRule(username, lyr_name)

                    print 'Done.'
                else:
                    print 'Invalid choice.'

    def handle_layer_option(self, all_layers, base_endpoint, count, response, token_key, token_params):
        if response.isdigit() and int(response) == count:
            des = raw_input('Enter a descriptor: ')
            public = raw_input('Is this a public layer (\'y\' or \'n\')? ')

            if public.lower() == 'y':
                public = True
            else:
                public = False

            r = requests.post(base_endpoint + '/layer/', params=token_params,
                              data=json.dumps({"des": des, "public": public}))
            print r.url
            print '\n'
            print r.text

        elif response.isdigit():
            layer = all_layers[int(response)]
            r = requests.get(base_endpoint + '/layer/{0}'.format(layer['uid']),
                             params=token_params)
            print 'Accessed endpoint: {0}'.format(r.url)
            print 'Layer: {0}\nUID: {1}'.format(layer['descriptor'], layer['uid'])

            menu_options = [
                '  1 - Add/remove permissions',
                '  2 - Export',
                '  3 - Delete',
                '  4 - Import'
            ]
            for each in menu_options:
                print each

            response = raw_input('Select a menu option (or \'q\' to go back): ').strip()

            if response == 'q':
                return

            self.handle_layer_activity(base_endpoint, layer, response, token_key, token_params)

        elif response.lower() == 'b':
            pass

        else:
            print 'Invalid option.'

    def handle_layer(self, base_endpoint, token_key, token_params):
        r = requests.get(base_endpoint + '/layer/', params=token_params)
        all_layers = r.json()
        print r.url
        print 'Layers'
        count = 0
        for i in xrange(len(all_layers)):
            print '  {0} - {1}'.format(i, all_layers[i]['descriptor'])
            count = i
        count += 1
        print '  {0} - {1}'.format(count, 'Create new layer')
        response = raw_input(
            'Select an option (or \'q\' to go back): ').strip()

        if response == 'q':
            return

        self.handle_layer_option(all_layers, base_endpoint, count, response, token_key, token_params)

    def handle_activity(self, response, token_key, token_params):
        base_endpoint = 'http://54.201.67.167:8000/rapid'

        if response == '1':
            self.print_tokens(base_endpoint)
        elif response == '2':
            self.handle_geoview(base_endpoint, response, token_key, token_params)
        elif response == '3':
            self.handle_layer(base_endpoint, token_key, token_params)

    def print_top_menu_options(self):
        print 'Available data and operations:'
        menu_options = [
            '  1 - API Tokens',
            '  2 - GeoViews',
            '  3 - Layers',
        ]
        for each in menu_options:
            print each

    def handle(self, *args, **options):
        setup_logging_to_file('ui_error_log.txt')

        print 'Hello. Welcome to RAPID.'

        token = self.get_token()

        if not token:
            print 'Goodbye.'
            return

        token_params = {'token': token.key}
        token_key = token.key

        while True:
            self.print_top_menu_options()

            response = raw_input('Select a menu option (or \'q\' to quit): ').strip()
            print ''

            if response.lower().strip() == 'q':
                print 'Goodbye!'
                return

            try:
                self.handle_activity(response, token_key, token_params)
            except Exception, e:
                print 'An error occurred. Technical details logged to ui_error_log.txt.\n'
                log_exception(e)