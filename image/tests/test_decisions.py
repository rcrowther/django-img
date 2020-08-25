from django.test import TestCase
from image import decisions
from image.image_filters import Thumb
from . import utils


# ./manage.py test image.tests.test_decisions
class TestImageSavePath(TestCase):
    def setUp(self):
        self.image = utils.get_test_image()
        
    def test_long_imagename_truncated(self):
        filepath = '/home/nightmare/originals/Cetron-DKZ800-Carphones-FurryDice-for-BMW-iPad-Fridge-Solidus-Nokirapo-MP3-players-etc-WITHOUT-Microphone-and-remote-0-2-uai-258x258.tiff'
        r = decisions.image_save_path(self.image, filepath)
        self.assertLessEqual(len(r), 100)    

    def tearDown(self):
        utils.image_delete(self.image)



class TestReformSavePAth(TestCase):
    def setUp(self):
        self.reform = utils.get_test_reform()        

    def test_long_reformname_truncated(self):
        filepath = '/home/nightmare/originals/Cetron-DKZ800-Carphones-FurryDice-for-BMW-iPad-Fridge-Solidus-Nokirapo-MP3-players-etc-WITHOUT-Microphone-and-remote-0-2-uai-258x258-twas-a-filter-name.bake.png.tiff'
        r = decisions.reform_save_path(self.reform, filepath)
        self.assertLessEqual(len(r), 100)         

    def tearDown(self):
        utils.reform_delete(self.reform)



class TestReformSaveInfo(TestCase):

    def test_src_wins(self):
        mock_args = {'file_format': None, 'jpeg_quality': 19}
        mock_filter = dict()
        
        # mocks have no opionion, so 'src' wins
        save_info = decisions.reform_save_info(mock_filter, 'jpg', mock_args)
        self.assertEqual(save_info['format'], 'jpg')  
            
    def test_filter_wins(self):
        mock_args = {'file_format': 'tiff', 'jpeg_quality': 19}
        
        # Thumb defines 'png' and wins
        save_info = decisions.reform_save_info(Thumb, 'jpg', mock_args)
        self.assertEqual(save_info['format'], 'png')  

    def test_model_attrs_wins(self):
        mock_args = {'file_format': 'tiff', 'jpeg_quality': 19}
        
        # Thumb has no opinion on 'quality', so args (from model) wins.
        save_info = decisions.reform_save_info(Thumb, 'jpg', mock_args)
        self.assertEqual(save_info['jpeg_quality'], 19) 
                
