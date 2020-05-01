import functools
from django.apps import apps
from django.conf import settings
from importlib import import_module
from image.decorators import register
from image.registry import registry

from image.filters import (
    Filter, Format, Resize, Crop, ResizeSmart, Thumb
)

__all__ = [
    "Format", "Resize", "Crop", "ResizeSmart", "Thumb",
    "register", "registry"
    ]
# See django.contrib.admin.__init__()
#def autodiscover():
#    autodiscover_modules('admin', register_to=site)


#default_app_config = 'django.contrib.admin.apps.AdminConfig'



# ['image', 'article', 'review']
#!self
def autodiscover_noncore_modules(*args, include=None):
    """
    Auto-discover INSTALLED_APPS but non-core modules
    Fails silently when not present. 
    Forces an import on the module to recover any requests.
    Very similar to django.utils.module_loading.autodiscover_modules,
    but it's not.
    @include add extra paths. These will not be loaded. May be used to 
    include self module, if the method is run from a module (self will
    fail loading, as it canot be seen)
    @args module names to find
    """
    from django.apps import apps

    r = []
    
    if (include):
        #for i in include:
        #    r = ['{}.{}'.format(i, name) for name in args]
        r = ['{}.{}'.format(include, name) for name in args]
        
    for app_config in apps.get_app_configs():
        app_path = app_config.name
        if (not app_path.startswith('django')):
            for module_name in args:
                # Attempt to import the app's module.
                try:
                    p = '{}.{}'.format(app_path, module_name)
                    print(p)
                    import_module(p)
                    r.append(p)
                except Exception as e:
                    print('autodisccover except:')
                    print(str(e))
                    pass
            
    return r


def autodiscover():
    print('image autodiscover')
    modules = autodiscover_noncore_modules('image_filters', include='image')
    

# @functools.lru_cache(maxsize=None)
# def get_filters():

