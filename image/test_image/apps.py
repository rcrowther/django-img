from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _



class TestImageConfig(AppConfig):
    name = 'test_image'
    verbose_name = _("Test Image")
    
    def ready(self):
        super().ready()
