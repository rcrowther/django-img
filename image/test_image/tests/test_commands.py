from django.test import TestCase
from django.core.management.base import CommandError
from image.management.commands import common
from test_image.models import TestImage, TestReform


# ./manage.py test image.tests.test_commands
class TestCommands(TestCase):

    def options(self, path):
        return {'model': path}
        
    def test_get_image_model_default(self):
        image_model = common.get_image_model(self.options(''))
        #self.assertEqual(image_model, TestImage) 
        self.assertEqual(image_model, None) 

    def test_get_image_model_shortpath_fails(self):
        with self.assertRaises(CommandError):        
            common.get_image_model(self.options('TestImage'))

    def test_get_image_model_longpath_fails(self):
        with self.assertRaises(CommandError):        
            common.get_image_model(self.options('django.image.Image'))

    def test_get_image_model_nonexistence_fails(self):
        with self.assertRaises(CommandError):        
            common.get_image_model(self.options('woozy.Perception'))

    def test_get_image_model_nonimage_fails(self):
        with self.assertRaises(CommandError):        
            common.get_image_model(self.options('test_image.TestReform'))
                                            
    def test_get_image_model(self):
        common.get_image_model(self.options('test_image.TestImage'))

##
    def test_get_reform_model_default(self):
        image_model = common.get_reform_model(self.options(''))
        #self.assertEqual(image_model, TestReform) 
        self.assertEqual(image_model, None) 

    def test_get_reform_model_shortpath_fails(self):
        with self.assertRaises(CommandError):        
            common.get_reform_model(self.options('TestReform'))

    def test_get_reform_model_longpath_fails(self):
        with self.assertRaises(CommandError):        
            common.get_reform_model(self.options('django.image.Reform'))

    def test_get_reform_model_nonexistence_fails(self):
        with self.assertRaises(CommandError):        
            common.get_reform_model(self.options('woozy.Perception'))

    def test_get_reform_model_nonreform_fails(self):
        with self.assertRaises(CommandError):        
            common.get_reform_model(self.options('test_image.TestImage'))
                                            
    def test_get_reform_model(self):
        common.get_reform_model(self.options('test_image.TestReform'))
