from django.core.management.base import BaseCommand, CommandError
from image.models import Image, Reform
import datetime



class Command(BaseCommand):
    help = 'List images'
    output_transaction = True
    
    def add_arguments(self, parser):

        parser.add_argument(
            '-c',
            '--contains',
            type=str,
            help='Search for titles containing this text',
        )

        parser.add_argument(
            '-w',
            '--weeks-back',
            type=int,
            help='Search for entries from now to "count" weeks back',
        )
                
                
    def handle(self, *args, **options):
        qs = Image.objects
        
        if (options["contains"]):
            #if (not options["contains"]):
                #raise CommandError("Value of --contains option reads empty?")            
            qs = qs.filter(title__icontains=options["contains"])
            
        if (options["weeks_back"]):
            week_num_now =  datetime.date.isocalendar(datetime.date.today())[1]
            
            if (options["weeks_back"] > week_num_now or options["weeks_back"] < 0):
                raise CommandError("Value of --weeks_back option cant be negative or larger than the year. Today is in week {}".format(week_num_now))             
            week_num_back = week_num_now - options["weeks_back"]
            qs = qs.filter(cdate__week__gte=week_num_back)
                
        qs = qs.values_list('pk', 'title', named=True)
        for e in qs:
            print("{} '{}'".format(e.pk, e.title))
