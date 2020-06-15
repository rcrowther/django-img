from django.test import TestCase
from image.settings import settings, Settings


# ./manage.py test image.tests.test_settings
class TestSettings(TestCase):
    # The class does a lot of checking itself.
    # Can do some default exists/functions checks
    
    def setUp(self):
        # get a defaulted Settings, uninfluenced by current app.
        self.settings = Settings(populate=False)
        #self.settings = settings

    #def test_file_path_originals(self):
    #    self.assertEqual(self.settings.file_path_originals, '...media/originals/')  

    def test_filename_originals_maxlen(self):
        self.assertGreater(self.settings.filename_originals_maxlen, 0)  

    def test_filename_reforms_maxlen(self):
        self.assertGreater(self.settings.filename_reforms_maxlen, 0) 

    def test_max_upload_size(self):
        self.assertEqual(self.settings.max_upload_size, None) 

