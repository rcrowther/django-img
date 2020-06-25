import unittest

from django.test import TestCase
from image.models import Image
from image.model_fields import ImageOneToOneField
from django.db import models

def mkImageField(model):
    return ImageOneToOneField(
                model,
                null=True, 
                blank=True,
                on_delete=models.CASCADE,
                related_name='+',
            )

def mkModel(model):
    i = mkImageField(model)
    attrs = {
    '__module__' : 'test', 
    'app_label': 'Test', 
    'img' : i
    }
    return  type('FieldTest', (models.Model,), attrs)

     
#! Build somehow. But needs Djago paraphenalia
class TestFields(TestCase):

    def test_non_model_raises(self):
        f = self.mkModel(image.filters.Filter)
        with self.assertRaises(Exception):
            f.check()
            
    def test_str_non_model_raises(self):
        f = self.mkModel('image.filters.Filter')
        with self.assertRaises(Exception):
            f.check()

            
    def test_non_image_model_raises(self):
        f = self.mkModel(models.Model)
        with self.assertRaises(Exception):
            f.check()

    def test_str_non_image_model_raises(self):
        f = self.mkModel('models.Model')
        with self.assertRaises(Exception):
            f.check()
            
    def test_image_model(self):
        f = self.mkModel(image.Image)
        f.check()
            
    def test_str_image_model(self):
        f = self.mkModel('image.Image')
        f.check()
