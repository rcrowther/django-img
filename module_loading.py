from importlib import import_module
from django.utils.module_loading import module_has_submodule
from django.apps import apps

def autodiscover_modules(
        *module_names, 
        parent_modules=[], 
        find_in_apps=True, 
        not_core_apps=False
    ):
    """
    Auto-discover named modules on module paths.
    Fails silently when not present. 
    Forces an import on the module to recover any requests.
    Very similar to django.utils.module_loading.autodiscover_modules,
    but it's not.
    
    module_names 
        module names to find
    parent_modules 
        hardcoded list of module paths to search
    find_in_apps 
        seek for modules in registered apps
    not_core_apps 
        remove 'django' paths from any given list
    return
        list of modules loaded
    """
    app_modules = []
    if (find_in_apps):
        app_modules = [a.name for a in apps.get_app_configs()]
    if (not_core_apps):
        app_modules = [p for p in app_modules if (not p.startswith('django'))]
    module_parents = [*parent_modules, *app_modules]
    r = []
    for module_parent in module_parents:
        for name in module_names:
            # Attempt to import the app's module.
            try:
                p = module_parent + '.' + name
                import_module(p)
                r.append(p)
            except Exception:
                # if the module doesn't exist, ignore the error, if
                # it does and threw an error, bubble up.
                if module_has_submodule(module_parent, name):
                    raise
    return r
