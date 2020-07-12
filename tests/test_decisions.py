from django.test import TestCase
from image import decisions

from image.image_filters import Thumb
from image.settings import settings, Settings
from .utils import get_test_image, get_test_reform


# ./manage.py test image.tests.test_decisions
class TestDecisions(TestCase):
    def setUp(self):
        # get a defaulted Settings, uninfluenced by current app.
        self.settings = Settings(populate=False)
        self.image = get_test_image()
        self.reform = get_test_reform()
        self.decisions = decisions
        
    def test_long_imagename_truncated(self):
        filepath = '/home/nightmare/originals/Cetron-DKZ800-Carphones-FurryDice-for-BMW-iPad-Fridge-Solidus-Nokirapo-MP3-players-etc-WITHOUT-Microphone-and-remote-0-2-uai-258x258.tiff'
        r = self.decisions.image_save_path(self.image, filepath)
        self.assertLessEqual(len(r), 100) 

    def test_long_reformname_truncated(self):
        filepath = '/home/nightmare/originals/Cetron-DKZ800-Carphones-FurryDice-for-BMW-iPad-Fridge-Solidus-Nokirapo-MP3-players-etc-WITHOUT-Microphone-and-remote-0-2-uai-258x258-twas-a-filter-name.bake.png.tiff'
        r = self.decisions.reform_save_path(self.reform, filepath)
        self.assertLessEqual(len(r), 100)         

    def test_save_decisions_filter_wins(self):
        mock_args = {'file_format': 'tiff', 'jpeg_quality': 19}
        
        # Thumb defines 'png' and wins
        save_info = self.decisions.reform_save_info(Thumb, 'jpg', mock_args)
        self.assertEqual(save_info['format'], 'png')  

    def test_save_decisions_model_attrs_wins(self):
        mock_args = {'file_format': 'tiff', 'jpeg_quality': 19}
        
        # Thumb has no opinion on 'quality', so args (from model) wins.
        save_info = self.decisions.reform_save_info(Thumb, 'jpg', mock_args)
        self.assertEqual(save_info['jpeg_quality'], 19) 
