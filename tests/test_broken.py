from django.test import TestCase
from image.shortcuts import get_reform_or_not_found
from image.models import Image
from image.image_filters import Thumb
from .utils import get_test_image_file_jpg


# ./manage.py test image.tests.test_broken
class TestShortcuts(TestCase):

    def setUp(self):
        self.filter = Thumb()

    def test_fallback(self):
        good_image = Image.objects.create(
            title="Test image",
            src=get_test_image_file_jpg(),
            auto_delete=Image.AutoDelete.YES,
        )
        reform = get_reform_or_not_found(good_image, self.filter)
        self.assertEqual(reform.src.name, 'reforms/test-image_thumb.png')
        good_image.delete()
    
    def test_fallback_to_not_found(self):
        bad_image = Image.objects.create(
            title="Test image",
            src=get_test_image_file_jpg(),
            auto_delete=Image.AutoDelete.YES,
        )

        bad_image.src.delete(False) 

        reform = get_reform_or_not_found(bad_image, self.filter)
        self.assertEqual(reform.src.name, 'unfound')
        bad_image.delete()
