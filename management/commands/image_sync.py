from django.core.management.base import BaseCommand
from image.models import Image
from pathlib import Path
from image.settings import settings



class Command(BaseCommand):
    help = 'Resync local image files to the database. The default (no options) adds models for orphan files.'
    output_transaction = True
    
    def add_arguments(self, parser):

        parser.add_argument(
            '--remove-orphaned-files',
            action='store_true',
            help='Delete orphaned files (the default is to register them)',
        )

        parser.add_argument(
            '--remove-orphaned-models',
            action='store_true',
            help='Delete orphaned models (with no matching file)',
        )        
        
    def fp_media_list(self):
        media_dir = settings.image_local_path
        
        # get all file paths
        return [f for f in media_dir.iterdir() if f.is_file()]

    def db_image_fp_list(self):
        ''' 
        Read all image model paths
        @return full-path Paths
        '''
        val_list = Image.objects.values_list('ifile', flat=True)
        media_full_path = Path(settings.media_root)
        
        return [media_full_path / rel_path for rel_path in val_list]
            

    def db_image_list(self):
        ''' 
        Read all image models for pk, title and file
        @return object list supplemented with 'full_path' key referencing a Path
        '''
        val_list = Image.objects.values('pk', 'title', 'ifile')
        media_full_path = Path(settings.media_root)
        for e in val_list:
            e['full_path']  = media_full_path / e['ifile']
        
        return  val_list  


    def handle(self, *args, **options):        
        ml = self.fp_media_list()

        if options['remove_orphaned_models']:            
            dbl = self.db_image_list()          
            model_no_file = [m for m in dbl if not(m['full_path'] in ml)]           
            pks = [m['pk'] for m in model_no_file]
                
            r = Image.objects.filter(pk__in=pks).delete()

            if (options['verbosity'] > 0):
                print("{} model(s) deleted".format(r[0])) 
            if (options['verbosity'] > 2):
                for m in model_no_file:
                    print(m['title'])
                    
        elif options['remove_orphaned_files']:
            count = 0
            fail = []
            
            dbl = self.db_image_fp_list()
            file_no_model = set(ml) - set(dbl)

            for path in file_no_model:
                try:
                    path.unlink()
                    count += 1
                except Exception:
                    fail.append(p)
                                        
            if (options['verbosity'] > 0):
                print("{} image(s) deleted".format(count)) 
                if (len(fail) > 0):
                    print("{} image(s) failed to delete. Path: '{}'".format(
                        len(fail),
                        "', '".join(fail),
                        )) 
        else:
            count = 0
            fail = []

            dbl = self.db_image_fp_list()
            file_no_model = set(ml) - set(dbl)

            for path in file_no_model:
                # Make new models.
                # Worth explaining:
                # How do we register orphaned files?
                # When the model is saved, the generated FieldFile will 
                # not recognise the file is stored and attempt a copy 
                # onto itself. This should fail silently, in linux, 
                # but Django throws a FileExistsError, then makes a 
                # renamed copy.
                # Preferebly, we would tell FieldFile the storage is 
                # committed. Interesingly, a simple string path, as 
                # opposed to an open File or Imagefile, assumes the
                # image is commited.
                
                # Presuming files in /media are already truncated by
                # configuration.
                # The update effect in Imagefiedls will not work with 
                # Paths, only strings
                i = Image(
                    title = path.stem,
                    ifile = str(path),
                ) 

                try:
                    i.save()
                    count += 1
                except Exception:
                    fail.append(p)
        
            if (options['verbosity'] > 0):
                print("{} image(s) created".format(count)) 
                if (len(fail) > 0):
                    print("{} image(s) failed import. Path: '{}'".format(
                        len(fail),
                        "', '".join(fail),
                        )) 
