from django.test import TestCase
from image.shortcuts import get_reform_or_not_found
from image.models import Image
from image.image_filters import Thumb
from .utils import get_test_image_file_jpg


class TestShortcuts(TestCase):
    def setUp(self):
        self.good_image = Image.objects.create(
            title="Test image",
            src=get_test_image_file_jpg(),
            auto_delete=True,
        )
        
    def test_fallback_to_not_found(self):
        filterthumb = Thumb()

        # good_image = Image.objects.create(
            # title="Test image",
            # src=get_test_image_file_jpg(),
        # )
        bad_image = Image.objects.get(id=1)

        rendition = get_reform_or_not_found(self.good_image, filterthumb)
        self.assertEqual(rendition.src.name, 'reforms/test-image_thumb.png')

        Reforms.objects.get(pk=1).src.delete(False) 

        rendition = get_reform_or_not_found(self.good_image, filterthumb)
        self.assertEqual(rendition.src.name, 'unfound')


    def tearDown(self):
        # delete
        self.good_image.delete(False) 
