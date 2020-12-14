from collections import Iterable 


class AlreadyRegistered(KeyError):
    pass


class NotRegistered(KeyError):
    pass
    
    
class Unregisterable(Exception):
    pass


class ClassRegistry:
    '''
    Simple registry.
    This is useful for locating code. Why do that when Python's import
    system is flexible and concise?
    Because you may wish to refer to code by string names. This is 
    relevant when code needs to be accessed from Django templates,
    where parameters are (mostly) strings.
    - Why not use a cached property?
    - Use decorators? 
    Because this allows targeted classes, so other code can be put in 
    the targetted modules.
    Does not handle permissions. 
    '''
    def __init__(self, name):
        # key -> class (not instance)
        self._registry = {} 
        self.name = name
                
    def register(self, k, klass):
        if k in self._registry:
            raise AlreadyRegistered('Already registered in {}. path:{}.{}'.format(
                self.name,
                klass.__module__,
                klass.__name__
            ))

        self._registry[k] = klass
                
    def unregister(self, k):
        """
        Unregister the given model(s).

        If a model isn't already registered, raise NotRegistered.
        """
        if k not in self._registry:
            raise NotRegistered('Class can not be unregistered {}'.format(k))
        del self._registry[k]

    def __call__(self, k, **kwargs):
        '''
        Return an instance of the registered class.
        '''
        f = None
        try:
            f = self._registry[k]
        except KeyError:
            raise NotRegistered("Class instance requested but not found. key:{} registered: {}".format(
            k,
            ", ".join(self.list.keys()),
            ))
        return f(**kwargs)
           
    @property
    def list(self):
        return self._registry

    @property
    def keys(self):
        return self._registry.keys()    
    
    @property
    def size(self):
        return len(self._registry)    
        
        
        
import image.filters

class FilterRegistry(ClassRegistry):
    def register(self, class_or_iterable):
        if (not isinstance(class_or_iterable, Iterable)):
            class_or_iterable = [class_or_iterable]
        for filter_class in class_or_iterable:
            if (not (issubclass(filter_class, image.filters.Filter))):
                raise Unregisterable("Is not a subclass of Filter class:{}.{}".format(
                    filter_class.__module__,
                    filter_class.__name__
                ))
            super().register(filter_class.human_id(), filter_class)

    def unregister(self, class_or_iterable):
        if (not isinstance(class_or_iterable, Iterable)):
            class_or_iterable = [class_or_iterable]
        for filter_class in class_or_iterable:
            super().unregister(filter_class.human_id())
      
registry = FilterRegistry('image.Filters')
