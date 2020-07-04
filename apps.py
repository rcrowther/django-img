from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
#from image.signals import register_file_delete_handlers
from django.core import checks
from image.checks import check_filters



# NB It would be custom to test for operation of depend libraries
# here, primarily Pillow. However, Django now does this for ImageFile.
# Also, the Wand files are boxed and optional import. So not a 
# concern.
class ImageConfig(AppConfig):
    name = 'image'
    label = 'image'
    verbose_name = _("Image handling")

    def ready(self):
        super().ready()
        self.module.autodiscover()
        
        #? why not explicit in admen when autodiscover used?
        checks.register(check_filters, 'image_filters')
        #from image.models import Image, Reform
        #register_file_delete_handlers(Image, Reform)
