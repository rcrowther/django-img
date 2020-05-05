from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from pathlib import Path
from image.constants import IMAGE_FORMATS

print('create settings')



# These are used in filters and site-wide Django settings.
# So gathered here.
def check_media_subpath(class_name, setting_name, v):
    if (v and (len(v) > 24)):
        raise ImproperlyConfigured(
            "In {}, '{}' value '{}' exceeds 24 chars."
            "Reset or set TRUNCATE_PATHS = False"
            " Path len (in chars): {}".format(
            class_name,
            setting_name,
            v,
            len(v),
        ))     

def check_image_formats(class_name, setting_name, v):
    if (v and (not(v in IMAGE_FORMATS))):
        raise ImproperlyConfigured(
            "In {}, '{}' value '{}' is unrecognised."
            " Recognised image formats: '{}'".format(
            class_name,
            setting_name,
            v,
            "', '".join(IMAGE_FORMATS),
        ))
        
def check_jpeg_quality(class_name, setting_name, v):
    if (v and (v < 1 or v > 100)):
        raise ImproperlyConfigured(
            "In {}, '{}' smust be 1--100."
            " Value: {}".format(
            class_name, 
            setting_name, 
            v
        ))    
    
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
        check_image_formats(
            'Django settings', 
            'IMG_FORMAT_OVERRIDE',
            self.format_override 
        )
        # impose short limit on filepath (Django, 100 char overall path default)
        # includes '/media/', so just 24 chars
        check_media_subpath(
            'Django settings', 
            'MEDIA_SUBPATH_REFORMS',  
            self.media_subpath_originals
        )                            
        check_media_subpath(
            'Django settings', 
            'MEDIA_SUBPATH_ORIGINALS',  
            self.media_subpath_reforms
        )
        check_jpeg_quality(
            'Django settings', 
            'IMG_JPEG_QUALITY', 
            self.jpeg_quality
        )
      
        
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
