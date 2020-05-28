from django.test import TestCase

from django.db import models
from image.models import Image
from image.model_fields import ImageSingleField
from image.form_fields import ModelFixedField
from .utils import get_test_image_file_jpg


    
# ./manage.py test image.tests.test_form_fields
class TestFormFields(TestCase):
    
    #def setUpTestData(cls):
    #    pass
        
    # Some, anyway
    def setUp(self):
        self.image = Image.objects.create(
            title="Test",
            src=get_test_image_file_jpg(),
            auto_delete=Image.AutoDelete.YES,
        )  
        mfield = ImageSingleField(
            Image,
            null=True, 
            blank=True,
            on_delete=models.CASCADE,
            related_name='+',
        )      
        self.form_field = ModelFixedField(mfield)

    def test_get_related_model(self):
        self.assertEqual(self.form_field.get_related_model(), Image)

    def test_get_related_model_fields(self):
        self.assertEqual(self.form_field.get_related_model_fields(), Image._meta.fields)   

    def test_get_objs(self):
        self.assertEqual(self.form_field.get_objs(1), self.image)  

    def test_prepare_value(self):
        self.assertEqual(self.form_field.prepare_value(5), 5)  

    def test_to_python(self):
        self.assertEqual(self.form_field.to_python(5), 5)  

    def test_has_changed(self):
        self.assertFalse(self.form_field.has_changed(5, 5)) 

    def test_has_changed_coerce_strings(self):
        self.assertFalse(self.form_field.has_changed(5, '5'))
        
    def test_has_changed_true(self):
        self.assertTrue(self.form_field.has_changed(5, 9)) 
        
    def has_changed_empty_vals(self):
        # both values are 'empty'
        self.assertFalse(self.form_field.has_changed({}, None)) 

    def tearDown(self):    
        self.image.src.delete(False) 
