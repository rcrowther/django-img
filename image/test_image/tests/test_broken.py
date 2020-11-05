from django.test import TestCase, TransactionTestCase
from image.shortcuts import get_reform_or_not_found
#from test_image.models import TestImage
from image.image_filters import Thumb
from pathlib import Path
from . import utils
import os 

# ./manage.py test image.tests.test_broken
# Image file deletion not set for base, so these require manual cleanup.
class TestShortcuts(TestCase):

    def setUp(self):
        self.filter = Thumb()

    def test_fallback_unused(self):
        image = utils.get_test_image()
        
        # This makes a reform (image file found)
        reform = get_reform_or_not_found(image, self.filter)
        os.remove(reform.src.path)
        utils.image_delete(image)
        name = Path(reform.src.name).name
        self.assertEqual(name, 'test-image_thumb.png')
    
    def test_fallback_not_found(self):
        image = utils.get_test_image()
        
        # delete file
        os.remove(image.src.path)
        image.src.delete(False)
                
        # This fails because no file
        reform = get_reform_or_not_found(image, self.filter)
        image.delete(False)
        stem = Path(reform.src.name).stem
        self.assertEqual(stem, 'unfound')

    def test_filter_none_raises_exception(self):
        # A more open case, using a call corrupt because it has no 
        # filter. This should cause an exception of some kind, not 
        # caught and rendered as a broken image by the shortcut (so the
        # lack of specifics)
        image = utils.get_test_image()
        with self.assertRaises(Exception):
            get_reform_or_not_found(image, None)
        utils.image_delete(image)
            
