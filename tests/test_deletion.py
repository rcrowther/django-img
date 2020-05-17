import unittest

from django.test import TestCase, TransactionTestCase
from image.models import Image, Reform, SourceImageIOError
from .utils import get_test_image_file_jpg
from pathlib import Path
from image.image_filters import Thumb



# ./manage.py test image.tests.test_deletion    
class TestDeletion(TransactionTestCase):
    def setUp(self):
        self.image = Image.objects.create(
            title="Test image",
            src=get_test_image_file_jpg(),
            auto_delete=Image.AutoDelete.YES,
        )
        
        self.filter = Thumb()
        
    def test_delete_image(self):
        self.image.delete()
        self.assertEqual(self.image.src, None)

    def test_reform(self):
        reform = self.image.get_reform(self.filter)
        p = Path(reform.src.path)
        self.image.delete()
        self.assertFalse(p.exists())


class TestPreservation(TestCase):
    def setUp(self):
        self.image = Image.objects.create(
            title="Test image",
            src=get_test_image_file_jpg(),
            auto_delete=Image.AutoDelete.NO,
        )

        self.filter = Thumb()

    def test_delete_image(self):
        p = Path(self.image.src.path)
        self.image.delete()
        self.assertTrue(p.exists())
        p.unlink() 

    def test_reform(self):
        reform = self.image.get_reform(self.filter)
        p = Path(self.image.src.path)
        pr = Path(reform.src.path)
        self.image.delete()
        self.assertFalse(pr.exists())        
        p.unlink() 
