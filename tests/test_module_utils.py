from django.test import TestCase
from image import module_utils
from django.core.exceptions import ImproperlyConfigured



# ./manage.py test image.tests.test_module_utils
class TestModuleUtils(TestCase):

    def test_get_model_no_data(self):
        with self.assertRaises(ImproperlyConfigured):
            module_utils.get_model('')
            
    def test_get_model_no_app(self):
        with self.assertRaises(ImproperlyConfigured):
            module_utils.get_model('Image')

    def test_get_model_with_app(self):
        module_utils.get_model('image.Image')
        
    def test_get_model_with_implicit_app(self):
        module_utils.get_model('Image', 'image')

    def test_get_image_model_not_image(self):
        with self.assertRaises(ImproperlyConfigured):
            module_utils.get_image_model('image.Thumb')

    def test_get_image_model(self):
        module_utils.get_image_model('image.Image')
