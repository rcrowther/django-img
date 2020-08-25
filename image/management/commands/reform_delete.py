from django.core.management.base import BaseCommand, CommandError
from . import common



class Command(BaseCommand):
    help = 'Automatically/bulk delete reform images'
    output_transaction = True

    def add_arguments(self, parser):
        common.add_model_argument(parser)
        common.add_contains_argument(parser)
        parser.add_argument(
            '--bulk',
            action='store_true',
            help='Delete reforms by SQL (fast, but less robust)',
        )
        
    def handle(self, *args, **options):
        Model = common.get_reform_model(options)
        qs = Model.objects.all()
        qs = common.filter_query_contains(options, qs)
        
        if options['bulk']:
            #! this going to work on relationship table? I hope so.
            r = qs.delete()
            if (options['verbosity'] > 0):
                print("{} reforms deleted".format(r[0])) 
        else:
            count = 0
            for im in qs:
                r = im.delete()
                
                # count from the return e.g. (1, {'weblog.Entry': 1})
                count += r[0]
                
            if (options['verbosity'] > 0):
                print("{} reforms deleted".format(count)) 
