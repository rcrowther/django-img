from django.core.management.base import BaseCommand, CommandError
from . import common


#! do a selective delete?
class Command(BaseCommand):
    help = 'Automatically/bulk delete images'
    output_transaction = True


    def add_arguments(self, parser):
        common.add_model_argument(parser)
        parser.add_argument(
            '--bulk',
            action='store_true',
            help='Delete images by SQL (fast, but less robust)',
        )

    def handle(self, *args, **options):
        Model = common.get_model(options, allow_reform=False)

        if options['bulk']:
            #! this going to work on reform relationship table? I hope so.
            r = Model.objects.all().delete()
            
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
            qs = Model.objects.all()
            for im in qs:
                r = im.delete()
                
                # count from return. May have failed!
                count += r[0]

            if (options['verbosity'] > 0):
                print("{} image(s) deleted".format(count)) 
