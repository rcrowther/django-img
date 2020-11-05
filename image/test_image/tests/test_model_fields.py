import unittest

from django.test import TestCase
from django.db import models
import test_image
from image.model_fields import ImageOneToOneField, ImageManyToOneField 

def mkImageOneToOneField():
    return ImageOneToOneField(
                test_image.models.TestImage,
            )

def mkImageManyToOneField():
    return ImageManyToOneField(
                test_image.models.TestImage,
            )
            
# def mkModel(model):
    # im = mkImageField(model)
    # attrs = {
    # '__module__' : 'test', 
    # 'app_label': 'Test', 
    # 'img' : im
    # }
    # return  type('FieldTest', (models.Model,), attrs)


# ./manage.py test image.tests.test_model_fields
# ./manage.py test image.tests.test_model_fields.TestFieldCreation
class TestFieldCreation(TestCase):

    def test_non_model_raises(self):
        iff = ImageOneToOneField(test_image.models.TestReform)
        with self.assertRaises(Exception):
            iff.check()
            
    def test_str_non_model_raises(self):
        iff = ImageOneToOneField('duff.Path')
        with self.assertRaises(Exception):
            iff.check()

    #def test_str_image_model(self):
        #iff = self.mkModel('image.Image')
        # f.check()




# ./manage.py test image.tests.test_model_fields            
class TestFields(TestCase):

    def setUp(self):
        self.iff = mkImageOneToOneField()
        self.iffm = mkImageManyToOneField()
            
    #def test_image_model(self):
    #    self.iff.check()
            
    def test_one_to_one_attrs(self):
        self.assertTrue(self.iff.blank)
        self.assertTrue(self.iff.null)
        self.assertTrue(self.iff.to_fields[0], 'id')
        self.assertEqual(self.iff.remote_field.related_name, '+')
        self.assertEqual(self.iff.remote_field.on_delete, models.SET_NULL)
        
    def test_many_to_one_attrs(self):
        self.assertTrue(self.iffm.blank)
        self.assertTrue(self.iffm.null)
        self.assertTrue(self.iffm.to_fields[0], 'id')
        self.assertEqual(self.iffm.remote_field.related_name, '+')
        self.assertEqual(self.iffm.remote_field.on_delete, models.SET_NULL)
