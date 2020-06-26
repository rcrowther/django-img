from django.test import TestCase, TransactionTestCase
from image.shortcuts import get_reform_or_not_found
from image.models import Image
from image.image_filters import Thumb
from .utils import get_test_image_file_jpg
from pathlib import Path

# ./manage.py test image.tests.test_broken
#! look in utils for model
class TestShortcuts(TransactionTestCase):

    def setUp(self):
        self.filter = Thumb()

    def test_fallback_image_found(self):
        good_image = Image.objects.create(
            title="Test image",
            src=get_test_image_file_jpg(),
        )
        reform = get_reform_or_not_found(good_image, self.filter)
        name = Path(reform.src.name).name
        self.assertEqual(name, 'test-image_thumb.png')
        good_image.delete(False)
    
    def test_fallback_to_not_found(self):
        bad_image = Image.objects.create(
            title="Test image",
            src=get_test_image_file_jpg(),
        )

        bad_image.src.delete(False) 
        
        # an instance of the model remains
        reform = get_reform_or_not_found(bad_image, self.filter)
        stem = Path(reform.src.name).stem
        self.assertEqual(stem, 'unfound')

    def test_filter_none_raises_exception(self):
        # A more open case, using a call corrupt because it has no 
        # filter. This should cause an exception of some kind, not 
        # caught and rendered as a broken image by the shortcut (so the
        # lack of specifics)
        bad_image = Image(
            title="Test image",
            auto_delete=Image.AutoDelete.YES,
        )
        with self.assertRaises(Exception):
            get_reform_or_not_found(bad_image, None)
            
