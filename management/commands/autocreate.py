from django.core.management.base import BaseCommand, CommandError
from image.models import Image
from image import utils
from django.conf import settings
from pathlib import Path
from django.core.files.images import ImageFile


class Command(BaseCommand):
    help = 'Automatically/bulk add images to the image app'

    #def add_arguments(self, parser):
    #    parser.add_argument('folder_name', nargs='+', type=int)

    def handle(self, *args, **options):
        # get the dir path of the image dir
        #originals_stub = utils.Settings().media_subpath_originals
        originals_stub = 'original_images'
        media_dir = ''
        if (hasattr(settings, 'MEDIA_ROOT')):
            media_dir = settings.MEDIA_ROOT
        else:
            raise CommandError('MEDIA_ROOT attribute not in settings?')
        
        originals_filepath = Path(media_dir) / originals_stub
        
        # get all file paths
        l = len(media_dir) + 1

        image_filepaths = [str(f.resolve())[l:] for f in originals_filepath.iterdir() if f.is_file()]
                #
                # make relative to the django directory
        print(str(image_filepaths))                
                
        # read all image model paths
        model_paths = Image.objects.values_list('ifile', flat=True)
        print('model_paths:')
        for f in model_paths: 
            print(f)

        # remove model paths from found paths
        #! simpler to do by filename? flat filestructure...
        untracked_images = [p for p in image_filepaths if (not (in model_paths))]
       
        # make models
        b = []
        for p in untracked_images:
            f = ImageFile(reform_buff, name=dst_fname)            

            b.append(Image(
                title = p.stem
                ifile = f,
                width =,
                height =,
                size = 
            )) 
        #raise CommandError('Poll "%s" does not exist' % poll_id)
        pass
