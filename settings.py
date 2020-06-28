from types import SimpleNamespace
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from pathlib import Path
from image.configuration_checks import (
    check_image_formats,
    check_jpeg_quality,
    #check_positive,
)

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
    
    path_truncate_len
    100 chars in the databaase
    https://docs.djangoproject.com/en/3.0/ref/models/fields/#filefield
    win32 255 overall length
    This module sets a 32 char limit on the path, and filename limits 
    are based on actual lengths.
    '''
    def __init__(self, populate=True):
        # defaults
        self.media_root = None
        self.modules = []
        self.app_dirs = False
        
        self.reforms = SimpleNamespace()
        self.reforms.format_override = None
        self.reforms.jpeg_quality = 85
        
        if (populate):
            self.populate()
                 
                
    def populate(self):
        if (not(hasattr(settings, 'MEDIA_ROOT'))):
            raise ImproperlyConfigured('The image app requires MEDIA_ROOT to be defined in settings.')
        self.media_root = settings.MEDIA_ROOT
            
        if (hasattr(settings, 'IMAGES')):
            isettings = settings.IMAGES[0]
            if ('APP_DIRS' in isettings):
                self.app_dirs = isettings['APP_DIRS']
            if ('REFORMS' in isettings):
                reforms = isettings['REFORMS']
                if ('FORMAT_OVERRIDE' in reforms):
                    self.reforms.format_override = reforms['FORMAT_OVERRIDE']
                    check_image_formats(
                        'Django settings', 
                        'REFORMS[FORMAT_OVERRIDE]',
                        self.reforms.format_override 
                    )  
                if ('JPEG_QUALITY' in reforms):
                    self.reforms.jpeg_quality = reforms['JPEG_QUALITY']
                    check_jpeg_quality(
                        'Django settings', 
                        'REFORMS[JPEG_QUALITY]', 
                        self.reforms.jpeg_quality
                    )                         
            if ('MODULES' in isettings):
                self.modules = isettings['MODULES']
            
    def __repr__(self):
        return "Settings( app_dirs:{}, modules:{}, reform_settings:{})".format(
            self.app_dirs,
            self.modules,
            self.reforms,
        )



# set one up
settings = Settings()
