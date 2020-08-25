import datetime

from django.core.management.base import BaseCommand, CommandError
from . import common



class Command(BaseCommand):
    help = 'List reforms. Default model is the core app.'
    output_transaction = True
    
    def add_arguments(self, parser):
        common.add_model_argument(parser)
        common.add_contains_argument(parser)
                
    def handle(self, *args, **options):
        Model = common.get_reform_model(options)
        qs = Model.objects
        qs = common.filter_query_contains(options, qs)

        for e in qs.all():
            print("{} {}".format(e.pk, e.src))
