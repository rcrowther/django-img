from django.utils.functional import cached_property
from django.apps import apps
from importlib import import_module

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
        return self.path[-1]
               
    @property
    def root(self):
        return self.path[0]
        
    @property
    def branch(self):
        if (self.size > 1):
            return ModulePath(*self.path[0:-1])
        else:
            raise IndexError('Can not return branch when length is one. elem:{}'.format(root))
            
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

    
