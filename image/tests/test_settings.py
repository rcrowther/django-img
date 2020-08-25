from django.test import TestCase
from django.core.exceptions import ImproperlyConfigured
from image.settings import settings, Settings


# ./manage.py test image.tests.test_settings
class TestSettings(TestCase):
    # Can do some default exists/functions checks
    
    def setUp(self):
        # get a defaulted Settings, uninfluenced by current app.
        self.settings = Settings(populate=True)

    #def test_no_media_root_raises_error(self):
    #    with self.assertRaises(ImproperlyConfigured):
    #        self.settings.media_root

    def test_broken(self):
        self.assertTrue(hasattr(self.settings, 'broken_image_path'))
                    
    def test_modules(self):
        self.assertTrue(type(self.settings.modules) == list)

    def test_app_dirs(self):
        self.assertTrue(type(self.settings.app_dirs)==bool)
  
