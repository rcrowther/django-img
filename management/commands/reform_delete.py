from django.core.management.base import BaseCommand, CommandError
from image.models import Image, Reform
from . import common



#! do a selective delete?
class Command(BaseCommand):
    help = 'Automatically/bulk delete reform images'
    output_transaction = True

    def add_arguments(self, parser):
        common.add_model_argument(parser)
        parser.add_argument(
            '--bulk',
            action='store_true',
            help='Delete reforms by SQL (fast, but less robust)',
        )
        
    def handle(self, *args, **options):
        Model = common.get_model(options, allow_reform=True)

        # hackety hack
        if (not issubclass(Model, Reform)):
            raise CommandError("Given class not a subclass of Reform: '{}'".format(options['model']))

        if options['bulk']:
            #! this going to work on relationship table? I hope so.
            r = Model.objects.all().delete()
            if (options['verbosity'] > 0):
                print("{} reforms deleted".format(r[0])) 
        else:
            # if (not(options['image_titles'])):
                # if (options['verbosity'] > 0):
                   # print('no args, very safe?')
            # else:
            count = 0
            qs = Model.objects.all()
            for im in qs:
                r = im.delete()
                
                # count from the return e.g. (1, {'weblog.Entry': 1})
                count += r[0]
                
            if (options['verbosity'] > 0):
                print("{} reforms deleted".format(count)) 
