from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from pathlib import Path

print('create settings')



class Settings():
    '''
    Gather settings from the settings file.
    For easy access and maybe caching. Django enables attribute access 
    on the Settings.py file, but it is awkward poking in for app-related
    settings.
    app_dirs 
    if false, use only the app-defined filters
    
    modules 
    module paths to seek an image_filters submodule 
    
    truncate_paths
    100 chars in the databaase
    https://docs.djangoproject.com/en/3.0/ref/models/fields/#filefield
    win32 255 overall length
    This module sets a 32 char limit on the path, and filename limits 
    are based on actual lengths.
    '''
    def __init__(self):
        # defaults
        self.media_root = None
        self.modules = []
        self.app_dirs = False
        self.media_subpath_originals = 'originals'
        self.media_subpath_reforms = 'reforms'
        self.format_override = None
        self.jpeg_quality = 85
        self.truncate_paths = True
        self.populate()
        
    @cached_property
    def path_length_limit(self):
        '''
        Length the settingss will allow for filenames.
        '''
        return (100 - max(len(self.media_subpath_originals), len(self.media_subpath_reforms)))
              
    @property
    def image_local_path(self):
        '''
        Full path to the image directory.
        This is for original image uploads, not reforms.
        '''
        #! put back
        #return Path(settings.MEDIA_ROOT) / self.media_subpath_originals
        return Path(settings.MEDIA_ROOT) / "original_images"
        

    #@cached_property
    def populate(self):
        
        #!? Ummm not for cloud storage
        if (not(hasattr(settings, 'MEDIA_ROOT'))):
            raise ImproperlyConfigured('The image app requires MEDIA_ROOT to be defined in settings.')
        self.media_root = settings.MEDIA_ROOT
            
        #AttributeError
        if (hasattr(settings, 'IMAGES')):
            isettings = settings.IMAGES[0]
            if ('APP_DIRS' in isettings):
                self.app_dirs = isettings['APP_DIRS']
            if ('MEDIA_SUBPATH_ORIGINALS' in isettings):
                self.media_subpath_originals = isettings['MEDIA_SUBPATH_ORIGINALS']
            if ('MEDIA_SUBPATH_REFORMS' in isettings):
                self.media_subpath_reforms = isettings['MEDIA_SUBPATH_REFORMS']
            if ('IMG_FORMAT_OVERRIDE' in isettings):
                self.format_override = isettings['IMG_FORMAT_OVERRIDE']
            if ('IMG_JPEG_QUALITY' in isettings):
                self.jpeg_quality = isettings['IMG_JPEG_QUALITY']
            if ('TRUNCATE_PATHS' in isettings):
                self.truncate_paths = isettings['TRUNCATE_PATHS']                
            if ('MODULES' in isettings):
                self.modules = isettings['MODULES']
             
        # Tests
        # impose 32 char limit on filepath (Django, 100 char overall path default)
        # include '/media/'
        if (self.truncate_paths and (len(self.media_subpath_originals) > 24)):
            raise ImproperlyConfigured(
                "Path in MEDIA_SUBPATH_ORIGINALS in IMAGES setting exceeds 24 chars."
                "Reset or set TRUNCATE_PATHS = False"
                " Path len:'{}'".format(len(self.media_subpath_originals)))     
                    
        if (self.truncate_paths and (len(self.media_subpath_reforms) > 24)):
            raise ImproperlyConfigured(
                "Path in MEDIA_SUBPATH_REFORMS in IMAGES setting exceeds 24 chars."
                "Reset or set TRUNCATE_PATHS = False"
                " Path len:'{}'".format(len(self.media_subpath_reforrms)))
                  
        # notdir_paths = [path for path in self.dirs if (not os.path.isdir(path))]
        # if (notdir_paths):
            # raise ImproperlyConfigured(
                # "Path(s) in DIR in IMAGES setting are not directories."
                # " Path(s):'{}'".format("', '".join(notdir_paths)))            
        
        
    def __str__(self):
        return "Settings({}, {}, {}, {}, {})".format(
            self.modules,
            ", ".join(self.app_dirs),
            self.media_subpath_originals,
            self.media_subpath_reforms,
            self.truncate_paths,
        )

# set one up
settings = Settings()
