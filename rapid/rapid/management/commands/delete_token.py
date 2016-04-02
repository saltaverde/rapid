from django.core.management import BaseCommand
from rapid.models import ApiToken

class Command(BaseCommand):
    def handle(self, *args, **options):

        print 'This utility deletes an existing API token.'

        token = None

        while not token:
            response = raw_input(
                'Enter a token\'s secret key for deletion (or \'q\' to quit). The action won\'t be performed yet: ')
            response = response.strip()

            if response== 'q':
                return
            elif len(response) == 0:
                continue
            else:
                key = response
                tokens = ApiToken.objects.filter(key__exact=key)
                if tokens.count() == 0:
                    print 'A token with this key doesn\'t exist. Try again.'
                    token = None
                else:
                    try:
                        print 'Hello'
                        token = list(tokens[:1])[0]
                        print 'Yo'
                        print token
                        print 'Found token: {0}'.format(token.descriptor)

                        response = raw_input('Are you sure you want to delete this token? (y or n): ')
                        response = response.strip()

                        if response.strip() == 'y':
                            token.delete()
                            print 'Token removed.'
                            return
                        else:
                            print 'Deletion canceled.'
                            return
                    except:
                        print 'There was a problem. Contact the system administrator.'
                        return






