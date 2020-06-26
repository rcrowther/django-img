from django.test import TestCase
from image import decisions

from image.image_filters import Thumb
from image.models import Image
from image.settings import settings, Settings
from .utils import get_test_image_file_jpg


# ./manage.py test image.tests.test_decisions
class TestDecisions(TestCase):
    def setUp(self):
        # get a defaulted Settings, uninfluenced by current app.
        self.settings = Settings(populate=False)
        self.decisions = decisions

    def test_long_imagename_truncated(self):
        filepath = '/home/nightmare/originals/Cetron-DKZ800-Carphones-FurryDice-for-BMW-iPad-Fridge-Solidus-Nokirapo-MP3-players-etc-WITHOUT-Microphone-and-remote-0-2-uai-258x258.tiff'
        r = self.decisions.image_save_path(filepath)
        self.assertLessEqual(len(r), 100) 

    def test_long_reformname_truncated(self):
        filepath = '/home/nightmare/originals/Cetron-DKZ800-Carphones-FurryDice-for-BMW-iPad-Fridge-Solidus-Nokirapo-MP3-players-etc-WITHOUT-Microphone-and-remote-0-2-uai-258x258-twas-a-filter-name.bake.png.tiff'
        r = self.decisions.reform_save_path(filepath)
        self.assertLessEqual(len(r), 100)         

    def test_save_decisions_filter_wins(self):
        # Thumb defines 'png'
        save_info = self.decisions.reform_save_info(Thumb, 'jpg')
        self.assertEqual(save_info['format'], 'png')  
