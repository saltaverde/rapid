from django.core.management import BaseCommand

from rapid.importer import Importer
from rapid.models import *
from rapid.select import *
from rapid.views import create_featuretype
from rapid.geofence import *
import rapid.gs as GS

import xml.etree.ElementTree as ET

import os

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


    def handle(self, *args, **options):

        print "Hello and welcome to the RAPID batch importer. We are glad you're here."

        token = self.get_token()

        if not token:
            print 'Goodbye.'
            return

        operator = DataOperator(token.key)
        importer = Importer(token.key)

        path = raw_input("Enter the directory to search: ")

        self.stdout.write("Searching all shapefiles, GeoJSON from {0}".format(path))

        self.stdout.write("The following ZIP archives were found:")
        zips = [z for z in os.listdir(path) if os.path.splitext(z)[1].lower() == '.zip']
        for z in zips:
            self.stdout.write(z)

        response = raw_input("\nDo you want to continue importing from this directory? (y/n)\n").strip()

        if response.lower().strip() == 'y':
            for z in zips:
                response = raw_input("Import {0}? y/n)".format(z)).strip().lower()
                if response == 'y':
                    descriptor = raw_input("Enter a descriptor for {0}\n".format(z))
                    is_public = raw_input("Is this layer public? (y/n)\n").strip()
                    if is_public.lower() == 'y':
                        is_public = True
                    else:
                        is_public = False

                    layer_uid = operator.create_layer(descriptor, is_public, None)
                    try:
                        importer.import_shapefile(os.path.join(path, z), layer_uid)

                        # Add featuretype to Geoserver
                        lyr_name = create_featuretype(layer_uid)
                        if lyr_name is None:
                            print 'WARNING: featureType {0} was not successfully sent to Geoserver'.format(layer_uid)
                            return

                        if is_public == True:
                            addGeofenceRule('*', lyr_name)
                        else:
                            username = token.descriptor
                            addGeofenceRule(username, lyr_name)
                    except:
                        print "Unable to import shapefile."
                else:
                    pass

        elif response.lower().strip() == 'n':
            pass

        self.stdout.write("All done!")

        return