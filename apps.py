from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.core import checks
from image.checks import check_filters



class ImageConfig(AppConfig):
    # NB It would be custom to test for operation of depend libraries
    # here, primarily Pillow. However, Django now does this for 
    # ImageFile. Also, the Wand files are boxed and optional import. So 
    # not a concern.
    name = 'image'
    verbose_name = _("Image handling")

    def ready(self):
        super().ready()
        self.module.autodiscover()        
        checks.register(check_filters, 'image_filters')
