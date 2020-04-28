#from image import ModelAdmin
#from django.contrib.admin.sites import site as default_site, AdminSite

from image.sites import site as default_site, ImagesSite
    
    
# from odeladmiin decoraters    
def register(*models, site=None):

    def _image_wrapper(filter_class):
        if not models:
            raise ValueError('At least one model must be passed to register.')

        admin_site = site or default_site

        if not isinstance(admin_site, Filter):
            raise ValueError('site must subclass Filter')

        if not issubclass(admin_class, Filter):
            raise ValueError('Wrapped class must subclass Filter.')

        image_site.register(models, filter_class=filter_class)

        return filter_class
    return _image_wrapper
