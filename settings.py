from types import SimpleNamespace
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from pathlib import Path
from image.constants import IMAGE_FORMATS

print('create settings')


# These settings checks are used in filters and site-wide Django 
# settings. So gathered here.
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
        
# keep it, but make it value range
def check_jpeg_quality(class_name, setting_name, v):
    if (v and (v < 1 or v > 100)):
        raise ImproperlyConfigured(
            "In {}, '{}' smust be 1--100."
            " value: {}".format(
            class_name, 
            setting_name, 
            v
        ))    
    
def check_value_range(class_name, setting_name, v, min, max):
    if (v and (v > min or v > max)):
        raise ValueError(
            "In {}, '{}' smust be {}--{}."
            " value: {}".format(
            class_name, 
            setting_name, 
            min,
            max,
            v
        )) 
         
def check_positive(class_name, setting_name, v):
    if (v and (v < 0)):
        raise ValueError(
            "In {}, '{}' must be a positive number."
            " value: {}".format(
            class_name, 
            setting_name, 
            v
        )) 

def check_boolean(class_name, setting_name, v):
    if (v and (not(type(v)==bool))):
        raise ValueError(
            "In {}, '{}' must be a boolean value."
            " value: {}".format(
            class_name, 
            setting_name, 
            v
        ))         

def check_file(class_name, setting_name, v):
    
    if (v and (not(Path(v).is_file()))):
        raise ValueError(
            "In {}, '{}' can not be deetected as an existing file"
            " value: {}".format(
            class_name, 
            setting_name, 
            v
        ))  
        
#! some confusion over avalue of settings here.
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
        
        self.reforms = SimpleNamespace()
        self.reforms.format_override = None
        self.reforms.jpeg_quality = 85
        self.reforms.truncate_paths = True
        
        self.auto_delete = False
        self.populate()
        
    #? could return none, if freed up in settings?
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
        For original image uploads, not reforms.
        '''
        #! put back
        #return Path(settings.MEDIA_ROOT) / self.media_subpath_originals
        return Path(self.media_root) / "original_images"
        

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
            if ('REFORMS' in isettings):
                reforms = isettings['REFORMS']
                if ('FORMAT_OVERRIDE' in reforms):
                    self.reforms.format_override = reforms['FORMAT_OVERRIDE']
                if ('JPEG_QUALITY' in reforms):
                    self.reforms.jpeg_quality = reforms['JPEG_QUALITY']
                if ('TRUNCATE_PATHS' in reforms):
                    self.reforms.truncate_paths = reforms['TRUNCATE_PATHS']    
            if ('AUTO_DELETE' in isettings):
                self.auto_delete = isettings['AUTO_DELETE']                             
            if ('MODULES' in isettings):
                self.modules = isettings['MODULES']
             
        # Tests

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
        check_image_formats(
            'Django settings', 
            'REFORMS[FORMAT_OVERRIDE]',
            self.reforms.format_override 
        )      
        check_jpeg_quality(
            'Django settings', 
            'REFORMS[JPEG_QUALITY]', 
            self.reforms.jpeg_quality
        )
                
    def __repr__(self):
        return "Settings( app_dirs:{}, modules:{}, {}, {}, reform_settings:{})".format(
            self.app_dirs,
            self.modules,
            self.media_subpath_originals,
            self.media_subpath_reforms,
            self.reforms,
        )



# set one up
settings = Settings()
