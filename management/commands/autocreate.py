from django.core.management.base import BaseCommand, CommandError
from image.models import Image

class Command(BaseCommand):
    help = 'Automatically/bulk add images to the image app'

    #def add_arguments(self, parser):
    #    parser.add_argument('folder_name', nargs='+', type=int)

    def handle(self, *args, **options):
        # get the dir path
        # read all image paths
        # add to image if not present
        #raise CommandError('Poll "%s" does not exist' % poll_id)
        pass
