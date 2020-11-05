from django.conf import settings as dsettings
from django.core.exceptions import ImproperlyConfigured


        
class Settings():
    '''
    Gather settings from the settings file.
    For easy access and maybe caching. Django enables attribute access 
    on the Settings.py file, but it is awkward poking in for app-related
    settings.
    
    app_dirs 
        if true, seek for image filters in registtered apps
    modules 
        module paths to seek image_filters modules 
    '''
    def __init__(self, populate=True):
        # defaults
        self.media_root = None
        self.modules = []
        self.app_dirs = True
        self.broken_image_path = 'image/unfound.png'
        if (populate):
            self.populate()
                 
    def populate(self):
        if (not(hasattr(dsettings, 'MEDIA_ROOT'))):
            raise ImproperlyConfigured('The image app requires MEDIA_ROOT to be defined in settings.')
        self.media_root = dsettings.MEDIA_ROOT
            
        if (hasattr(dsettings, 'IMAGES')):
            s = dsettings.IMAGES[0]
            if ('BROKEN' in s):
                self.broken_image_path = s['BROKEN']
            if ('SEARCH_APP_DIRS' in s):
                self.app_dirs = s['SEARCH_APP_DIRS']
            if ('SEARCH_MODULES' in s):
                self.modules = s['SEARCH_MODULES']
            
    def __repr__(self):
        return "Settings( app_dirs:{}, modules:{})".format(
            self.app_dirs,
            self.modules,
        )

# set one up
settings = Settings()
