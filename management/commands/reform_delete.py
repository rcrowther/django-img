from django.core.management.base import BaseCommand, CommandError
from image.models import Image, Reform



class Command(BaseCommand):
    help = 'Automatically/bulk delete reform images'
    output_transaction = True

    def add_arguments(self, parser):
        #parser.add_argument('image_titles', nargs='*', type=str)

        parser.add_argument(
            '--bulk',
            action='store_true',
            help='Delete reforms by SQL (fast, but less robust)',
        )
        
    def handle(self, *args, **options):
        if options['bulk']:
            #! this going to work on relationship table? I hope so.
            r = Reform.objects.all().delete()
            if (options['verbosity'] > 0):
                print("{} reforms deleted".format(r[0])) 
        else:
            # if (not(options['image_titles'])):
                # if (options['verbosity'] > 0):
                   # print('no args, very safe?')
            # else:
            count = 0
            qs = Reform.objects.all()
            for im in qs:
                r = im.delete()
                
                # count from the return e.g. (1, {'weblog.Entry': 1})
                count += r[0]
                
            if (options['verbosity'] > 0):
                print("{} reforms deleted".format(count)) 
