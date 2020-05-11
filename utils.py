from django.utils.functional import cached_property
from django.apps import apps
from importlib import import_module
from image.settings import settings
from pathlib import Path
from unidecode import unidecode
import os.path
print('create utils')



#! should match names with pathlib.Path
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
    def size(self):
        return len(self.path)
        
    @property
    def leaf(self):
        return ModulePath(self.path[-1])
               
    @property
    def root(self):
        return ModulePath(self.path[0])
        
    @property
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
    #print('module load ')
    #print(str(module_parents))
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

    
#? should be in decisions?
def image_save_path(filename):
    '''
    Get the full path from a filepath.
    This calculates and truncates lengths. For example, the stock 
    Django DB Filefield allows 100 chars path length. And Win32 
    operating systems can only handle 255 char path lengths. 
    @path a pathlib Path 
    '''
    p = Path(filename)
    
    # upload_to recieves a filename, no path.
    # This needs maybe truncation
    # do a unidecode in the filename and then replace non-ascii 
    # characters in filename with _ , to sidestep issues with filesystem encoding
    safer_stem = "".join((i if ord(i) < 128 else '_') for i in unidecode(p.stem))
        
    if (settings.reforms.truncate_paths):
        # truncate filename to prevent it going over 100 chars,
        # accounting for declared paths
        # https://code.djangoproject.com/ticket/9893        
        safer_stem = safer_stem[:settings.path_length_limit]
        
    #!? don't throw error, let other code handle?
    return os.path.join(settings.media_subpath_originals, safer_stem) + '.' + p.suffix
    
    
def reform_filename(path, filter_instance, extension):
    '''
    Get the save path from a filepath.
 
    @path a pathlib Path 
    '''
    # The path that comes in is from images. So it is mangled, and 
    # already truncated.
    # However, need to add a filter id to uniquify (if not perfectly), 
    # reduce collisions, make human readable, etc.
    # Then we need to put the extension on, which may have been changed 
    # in the filter.
    p = Path(path)

    dst_fname = "{}-{}.{}".format(
        p.stem,
        filter_instance.id_str_short(),
        extension
    )

    return dst_fname
    
    
def reform_save_path(filename):
    p = Path(filename)
    
    # upload_to recieves a filename, no path.
    stem = p.stem
    if (settings.truncate_paths):
        # truncate filename to prevent it going over 100 chars,
        # accounting for declared paths
        # https://code.djangoproject.com/ticket/9893        
        stem = stem[:settings.path_length_limit]
        
    # This needs the full path building.
    return os.path.join(settings.media_subpath_reforms, stem)  + '.' + p.suffix
