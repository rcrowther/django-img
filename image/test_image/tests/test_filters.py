from django.test import TestCase

from image.filters import Filter, PlacementError
from image.image_filters import Thumb



# Tests the class for attributes and checks, not the action.
class TestFilters(TestCase):
    def setUp(self):
        self.filter = Filter()
        self.filterthumb = Thumb()

    def test_human_id(self):
        self.assertEqual(self.filterthumb.human_id(), 'image.Thumb')
        
    def test_path_info_on_non_image_filter_module_raises_placementerror(self):
        with self.assertRaises(PlacementError):
            self.filter.human_id()
            
    def test_filename(self):
        basename = 'test'
        extension = 'png'
        self.assertEqual(self.filterthumb.filename(basename, extension), 'test-image_thumb.png')

