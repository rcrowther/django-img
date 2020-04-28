from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from . import checks  # NOQA


class ImageConfig(AppConfig):
    name = 'image'
    label = 'image'
    verbose_name = _("Image handling")

    #def ready(self):
    #    from images.signal_handlers import register_signal_handlers
    #    register_signal_handlers()
