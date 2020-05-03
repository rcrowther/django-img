from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import cached_property
from django.apps import apps
from importlib import import_module
import os.path


def module_path_root(module_path):
    #! should return nothing on fail?
    idx = module_path.find('.') 
    if (idx >= 0):
        return module_path[:idx]
    return module_path
    
def module_path_leaf(module_path):
    idx = module_path.rfind('.') 
    if (idx >= 0 and (len(module_path) > idx + 1)):
        return module_path[idx + 1:]
    return module_path 

def module_path_branch(module_path):
    idx = module_path.rfind('.') 
    if (idx >= 0):
        return module_path[:idx]
    return module_path 

def module_path_append(module_path, leaf):
    return "{}.{}".format(module_path, leaf)



class ModulePath():
    '''
    Path-like class for handling import/module patths.
    '''
    @classmethod
    def from_str(class_object, str_path):
        '''Call as
           d = ModulePath.from_str('graphic.effect.zoom')
        '''
        return class_object(*str_path.split('.'))
        
    def __init__(self, *args):
        self.path = args
        
    @property
    def leaf(self):
        return self.path[-1] 
               
    @property
    def root(self):
        return self.path[0]
        
    def branch(self):
        return ModulePath(*self.path[0:-1])

    def extend(self, new_leaf):
        return ModulePath(*self.path, new_leaf)
        
    @property
    def str(self):
        return self.__str__()
        
    def __repr__(self):
        return 'ModulePath("{}")'.format('", "'.join(self.path))
        
    def __str__(self):
        return ".".join(self.path)
        

def autodiscover(
    *module_names, 
    parents=[], 
    find_in_apps=True, 
    not_core_apps=False
    ):
    """
    Auto-discover modules on module pathss.
    Fails silently when not present. 
    Forces an import on the module to recover any requests.
    Very similar to django.utils.module_loading.autodiscover_modules,
    but it's not.
    @module_names module names to find
    @parents list of module paths to search
    @find_in_apps seek for modules in registered apps
    @not_core_apps remove 'django' paths from any given list
    """
    app_modules = []
    if (find_in_apps):
        app_modules = [a.name for a in apps.get_app_configs()]
    if (not_core_apps):
        app_modules = [p for p in app_modules if (not p.startswith('django'))]
    module_parents = [*parents, *app_modules]
    print('module load ')
    print(str(module_parents))
    r = []
    for module_parent in module_parents:
        for name in module_names:
            # Attempt to import the app's module.
            try:
                p = ModulePath(module_parent).extend(name).str
                import_module(p)
                r.append(p)
            except Exception as e:
                print("exception on {} {}".format(p, e))
                pass
            
    return r

#class InvalidTemplateEngineError(ImproperlyConfigured):
#    pass
    
class Settings():
    def __init__(self):
        #self._settings = None
        self.modules = []
        self.app_dirs = False
        self.media_subpath_originals = 'originals'
        self.media_subpath_reforms = 'reforms'
        self.populate()

    #@cached_property
    def populate(self):
        #AttributeError
        print('settings')
        if (hasattr(settings, 'IMAGES')):
            isettings = settings.IMAGES[0]
            print('isettings')
            print(str(isettings))
            if ('APP_DIRS' in isettings):
                self.app_dirs = isettings['APP_DIRS']
            if ('MEDIA_SUBPATH_ORIGINALS' in isettings):
                self.media_subpath_originals = isettings['MEDIA_SUBPATH_ORIGINALS']
            if ('MEDIA_SUBPATH_REFORMS' in isettings):
                self.media_subpath_reforms = isettings['MEDIA_SUBPATH_REFORMS']
            if ('MODULES' in isettings):
                self.modules = isettings['MODULES']
                

        #? tests
        # notdir_paths = [path for path in self.dirs if (not os.path.isdir(path))]
        # if (notdir_paths):
            # raise ImproperlyConfigured(
                # "Path(s) in DIR in IMAGES setting are not directories."
                # " Path(s):'{}'".format("', '".join(notdir_paths)))            
        
        
    def __str__(self):
        return "Settings({}, {}, {}, {})".format(
            self.modules,
            ", ".join(self.app_dirs),
            self.media_subpath_originals,
            self.media_subpath_reforms,
        )
