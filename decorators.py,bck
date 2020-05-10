# from modeladmiin decoraters    
def register(*classes):
    """
    Register the given classes and wrapped ModelAdmin class with
    admin site:

    @register(Author)
    class AuthorAdmin(admin.ModelAdmin):
        pass
    """
    from image import Filter
    from image.registry import registry

    def _image_wrapper():
        print('decor inner'.format(str(classes)))
        if not classes:
            raise ValueError('At least one class must be passed to register.')

        #if not issubclass(filter_class, Filter):
        #    raise ValueError('Registered class must subclass Filter.')
            
        registry.register(classes)

        return filter_class
    print('decor')        
    return _image_wrapper
