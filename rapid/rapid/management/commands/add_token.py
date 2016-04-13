from django.core.management import BaseCommand
from rapid.models import ApiToken

class Command(BaseCommand):
    def handle(self, *args, **options):

        print 'This utility creates a new, secret API token, which is required when making permission-dependent API calls.'
        print 'The following tokens already exist:'

        if ApiToken.objects.all().count() > 0:
            for token in ApiToken.objects.all():
                print '  {0}'.format(token.descriptor)
        else:
            print '  [No tokens]'
        print ''

        descriptor = None

        while not descriptor:
            response = raw_input(
                'Enter a public name or descriptor for the new token (or enter \'q\' to quit): ')
            response = response.strip()

            if response.strip() == 'q':
                return
            elif len(response.strip()) == 0:
                continue
            else:
                descriptor = response
                if ApiToken.objects.filter(descriptor__iexact=descriptor).count() > 0:
                    print 'An API token with this descriptor already exists. Try again.'
                    descriptor = None
                else:
                    try:
                        token = ApiToken()
                        token.setup(descriptor)
                        token.save()
                        print 'Token created. Record the following key in a safe place:'
                        print token.key
                        print ''
                    except:
                        print 'There was a problem. Contact the system administrator.'
                        return






