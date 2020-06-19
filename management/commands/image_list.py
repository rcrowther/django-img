import datetime

from django.core.management.base import BaseCommand, CommandError
from . import common



class Command(BaseCommand):
    help = 'List images. Default model is the core app.'
    output_transaction = True
    
    def add_arguments(self, parser):
        common.add_model_argument(parser)
        parser.add_argument(
            '-c',
            '--contains',
            type=str,
            help='Search for filenames containing this text',
        )
        parser.add_argument(
            '-w',
            '--weeks-back',
            type=int,
            help='Search for entries from now to "count" weeks back',
        )
                
                
    def handle(self, *args, **options):
        Model = common.get_model(options, allow_reform=True)

        qs = Model.objects
        
        if (options["contains"]):
            #if (not options["contains"]):
                #raise CommandError("Value of --contains option reads empty?")            
            qs = qs.filter(src__icontains=options["contains"])
            
        if (options["weeks_back"]):
            week_num_now =  datetime.date.isocalendar(datetime.date.today())[1]
            
            if (options["weeks_back"] > week_num_now or options["weeks_back"] < 0):
                raise CommandError("Value of --weeks_back option cant be negative or larger than the year. Today is in week {}".format(week_num_now))             
            week_num_back = week_num_now - options["weeks_back"]
            qs = qs.filter(upload_date__week__gte=week_num_back)
                
        #qs = qs.values_list('pk', 'src', named=True)
        for e in qs.all():
            print("{} {}".format(e.pk, e.filename))
