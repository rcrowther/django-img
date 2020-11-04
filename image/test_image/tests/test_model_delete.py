import unittest

from django.test import TestCase, TransactionTestCase
from image.models import Image, Reform, SourceImageIOError
from . import utils
from pathlib import Path
from image.image_filters import Thumb



# ./manage.py test image.tests.test_model_delete
#! how to override policy? Create new model?
class TestModelDeletionPolicy(TransactionTestCase):
    def setUp(self):
        self.image = utils.get_test_image()
        
    #def test_delete_image_delete_src(self):
    #    self.image.delete()
    #    self.assertEqual(self.image.src.path, None)

    def test_file_exists(self):
        im = utils.get_test_image()
        im.delete()
        p = Path(im.src.path)
        self.assertTrue(p.exists())
        p.unlink() 
        
    # def test_reform(self):
        # rm = utils.get_reform(self.filter)
        #utils.image_delete()
        # p = Path(rm.src.path)
        # self.i.delete()
        # self.assertFalse(p.exists())

        
    def tearDown(self):
        utils.image_delete(self.image)





    # def test_reform(self):
        # reform = self.image.get_reform(self.filter)
        # p = Path(self.image.src.path)
        # pr = Path(reform.src.path)
        # self.image.delete()
        # self.assertFalse(pr.exists())        
        # p.unlink() 
