from django.core.management.base import BaseCommand, CommandError
from django.core.files.images import ImageFile
from image.models import Image
from pathlib import Path
from image import file_utils


class Command(BaseCommand):
    help = 'Automatically/bulk add images to the image app'

    def add_arguments(self, parser):
        parser.add_argument('src_path', type=str)
                            
    def handle(self, *args, **options):
        # get the paths of src dir
        src_path = options['src_path']
        src_dir = Path(src_path)
        if (not(src_dir.is_dir())):
            raise CommandError("Source provided is not recognised as a directory. path: '{}'".format(src_path))
        
        # get paths of files in the src dir
        src_filepaths = [f.resolve() for f in src_dir.iterdir() if f.is_file()]
       
        # build models and save
        # I think we can not use bulk_create because we want to be 
        # causious as suceed as much as possible
        count = 0
        fail = []
        for path in src_filepaths:
            with open(path, 'rb') as f:
                fname = file_utils.filename(path) 
                i = Image(
                    title = fname,
                    ifile = ImageFile(f, name=fname + path.suffix),
                ) 
                try:
                    i.save()
                    count += 1
                except Exception:
                    fail.append(p)
        
        # output some results            
        if (options['verbosity'] > 0):
            print("{} image(s) created".format(count)) 
            if (len(fail) > 0):
                print("{} image(s) failed import. Paths: '{}'".format(
                    len(fail),
                    "', '".join(fail),
                    )) 
