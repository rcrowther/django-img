from types import SimpleNamespace
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from pathlib import Path
from image.configuration_checks import (
    check_media_subpath,
    check_image_formats,
    check_jpeg_quality,
    check_positive,
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
        self._max_upload_size = None
        self.media_subpath_originals = 'originals'
        self.media_subpath_reforms = 'reforms'
        
        self.reforms = SimpleNamespace()
        self.reforms.format_override = None
        self.reforms.jpeg_quality = 85
        self.reforms.truncate_paths = True
        
        self.auto_delete = False
        self.populate()

    @property
    def file_path_originals(self):
        '''
        Full path to the image directory.
        For original image uploads, not reforms.
        '''
        return Path(settings.media_root) / self.media_subpath_originals

    @property
    def filepath_maxlen(self):
        '''
        Length the settings will allow for filenames.
        If not trucating paths, then set large.
        '''
        # These default to something, if settings are None
        return  max(len(self.media_subpath_originals), len(self.media_subpath_reforms))
        
        
    @property
    def max_upload_size(self):
        # Convert figure to MB
        return self._max_upload_size * 10 * 1024 * 1024
                
    def populate(self):
        if (not(hasattr(settings, 'MEDIA_ROOT'))):
            raise ImproperlyConfigured('The image app requires MEDIA_ROOT to be defined in settings.')
        self.media_root = settings.MEDIA_ROOT
            
        #AttributeError
        if (hasattr(settings, 'IMAGES')):
            isettings = settings.IMAGES[0]
            if ('APP_DIRS' in isettings):
                self.app_dirs = isettings['APP_DIRS']
            if ('MAX_UPLOAD_SIZE' in isettings):
                self._max_upload_size = isettings['MAX_UPLOAD_SIZE']
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
        check_positive(
            'Django settings', 
            'MAX_UPLOAD_SIZE', 
            self._max_upload_size   
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
