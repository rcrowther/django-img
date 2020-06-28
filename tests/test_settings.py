from django.test import TestCase
from image.settings import settings, Settings


# ./manage.py test image.tests.test_settings
class TestSettings(TestCase):
    # The class does a lot of checking itself.
    # Can do some default exists/functions checks
    
    def setUp(self):
        # get a defaulted Settings, uninfluenced by current app.
        self.settings = Settings(populate=False)

