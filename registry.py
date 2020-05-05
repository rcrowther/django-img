from collections import Iterable 


class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


class ClassRegistry:
    '''
    Simple registry.
    This is useful for locating code. Why do that when Python's import
    system is flexible and concise?
    Because you may wish to refer to code by string names. This is 
    relevant when code needs to be accessed from Django templates,
    where parameters are (mostly) strings.
    Because
    Why not use a cahed property?
    Why use decorators? 
    Because this allows targeted classes, so other code can be put in 
    the targetted modules.
    Does not handle permissions. 
    '''
    def __init__(self, name='admin'):
         # model_class class -> admin_class instance
        self._registry = {} 
        self.name = name

    #def preload(self, ):
    def module_path(self, klass):
        return "{}.{}".format(klass.__module__, klass.__name__)
        
    def id_path(self, klass):
        app_path = klass.__module__[:klass.__module__.index('.')]
        return "{}.{}".format(app_path, klass.__name__)
                
    def register(self, class_or_iterable):

        #print('regestering')
        #print(str(class_or_iterable))
        if (not isinstance(class_or_iterable, Iterable)):
            model_or_iterable = [class_or_iterable]
        for klass in class_or_iterable:
            #if klass._meta.abstract:
            #    raise ImproperlyConfigured(
            #        'A class is abstract, so it cannot be registered. Classname: {}'.format(klass.__name__)
            #    )

            if klass in self._registry:
                registered_admin = str(self._registry[klass])
                msg = 'The model %s is already registered ' % klass.__name__
                # if registered_admin.endswith('.ModelAdmin'):
                    # # Most likely registered without a ModelAdmin subclass.
                    # msg += 'in app %r.' % re.sub(r'\.ModelAdmin$', '', registered_admin)
                # else:
                    # msg += 'with %r.' % registered_admin
                raise AlreadyRegistered(msg)

            # Ignore the registration if the model has been
            # swapped out.
            #if not klass._meta.swapped:
                # Instantiate the admin class to save in the registry
            # <path> => code
            self._registry[self.id_path(klass)] = klass
                
    def unregister(self, class_or_iterable):
        """
        Unregister the given model(s).

        If a model isn't already registered, raise NotRegistered.
        """
        if isinstance(class_or_iterable, ModelBase):
            class_or_iterable = [class_or_iterable]
        for klass in class_or_iterable:
            path = self.module_path(klass)
            if path not in self._registry:
                raise NotRegistered('Class can not be unregistered {}'.format( model.__name__))
            del self._registry[path]


    def get_instance(self, filter_id_path):
        f = None
        try:
            f = self._registry[filter_id_path]()
        except KeyError:
            raise NotRegistered("Filter definition requested but not found. Filter id:{} registered: {}".format(
            filter_id_path,
            ", ".join(self.list().keys()),
            ))
        return f 
        
        
    def list(self):
        return self._registry
        
        
print('create registry')
registry = ClassRegistry()
