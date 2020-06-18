from django.core.management.base import BaseCommand, CommandError
from image.models import Image, Reform



class Command(BaseCommand):
    help = 'Automatically/bulk delete images'
    output_transaction = True


    def add_arguments(self, parser):
        #parser.add_argument('image_titles', nargs='*', type=str)

        parser.add_argument(
            '--bulk',
            action='store_true',
            help='Delete images by SQL (fast, but less robust)',
        )

        
    def handle(self, *args, **options):
        if options['bulk']:
            #! this going to work on reform relationship table? I hope so.
            r = Image.objects.all().delete()
            
            if (options['verbosity'] > 0):
                print("{} image(s) deleted".format(r[0])) 
        else:
            # if (not(options['image_titles'])):
                # if (options['verbosity'] > 0):
                   # print('no args, very safe?')
            # else:
            count = 0
            #for ititle in options['image_titles']:
            #    r = Image.objects.filter(title=ititle).delete()
                # count from return. May have failed!
            #    count += r[0]
            qs = Image.objects.all()
            for im in qs:
                r = im.delete()
                
                # count from return. May have failed!
                count += r[0]

            if (options['verbosity'] > 0):
                print("{} image(s) deleted".format(count)) 
