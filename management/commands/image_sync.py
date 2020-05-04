
from django.core.management.base import BaseCommand, CommandError
from image.models import Image
#from image import utils
from pathlib import Path
from django.core.files.images import ImageFile
from image import file_utils

        #originals_stub = utils.Settings().media_subpath_originals
        #print(str(options))
        
    # def media_list(self):
        # media_dir = ''
        # if (hasattr(settings, 'MEDIA_ROOT')):
            # media_dir = settings.MEDIA_ROOT
        # else:
            # raise CommandError('MEDIA_ROOT attribute not in settings?')
            
        # originals_stub = 'original_images'
        # originals_filepath = Path(media_dir) / originals_stub
        # # get all file paths
        # l = len(media_dir) + 1

        # image_filepaths = [str(f.resolve())[l:] for f in originals_filepath.iterdir() if f.is_file()]
                # #
                # # make relative to the django directory
        # print(str(image_filepaths))  

    # def db_image_list(self):
        # # read all image model paths
        # model_paths = Image.objects.values_list('ifile', flat=True)
        # print('model_paths:')
        # for f in model_paths: 
            # print(f)

        # remove model paths from found paths
        #! simpler to do by filename? flat filestructure...
        #untracked_images = [p for p in image_filepaths if (not (p in model_paths))] 
