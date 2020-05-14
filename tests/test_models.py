import unittest

from django.test import TestCase
from image.models import Image, Reform, SourceImageIOError
from .utils import get_test_image_file_jpg



# ./manage.py test image.tests
# A fundamental issue throughout the tests is that image uploading 
# shunts files about. But TestCase will not complete over transactions
# So fails to trigger file deletion. So these tests are littered
# with rearDown() methods to clean up orphaned test files (poor orphans,
# unwanted...). 
class TestImage(TestCase):
    def setUp(self):
        self.image = Image.objects.create(
            title="Test image",
            src=get_test_image_file_jpg(),
            auto_delete=True,
        )

    def test_src_name(self):
        self.assertEqual(self.image.src.name, 'originals/test.jpg')
                
    def test_is_portrait(self):
        self.assertFalse(self.image.is_portrait())

    def test_is_landscape(self):
        self.assertTrue(self.image.is_landscape())
        
    def test_is_stored_locally(self):
        self.assertTrue(self.image.is_stored_locally())

    def test_bytesize(self):
        size = self.image.bytesize
        self.assertIsInstance(size, int)
        self.assertGreater(size, 0)
        
    def test_bytesize_on_missing_file_raises_sourceimageioerror(self):
        self.image.src.delete(save=False)
        with self.assertRaises(SourceImageIOError):
            self.image.bytesize

    def tearDown(self):    
        self.image.src.delete(False) 


from image.filters import Filter, PlacementError
from image.image_filters import Thumb

class TestFilters(TestCase):
    def setUp(self):
        # Create Filters for running tests on
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




from image.registry import (
    FilterRegistry, 
    AlreadyRegistered, 
    Unregisterable,
    NotRegistered
)

class NonFilter():
    pass
    
class TestFilterRegistry(TestCase):
    #! ignore non-image_config keys?
    def setUp(self):
        # Create a Registy for running tests on
        self.registry = FilterRegistry('test')

        # mock class to enter. NB, classes not instances
        self.filter = Thumb
        self.non_filter = NonFilter
        
    def test_register(self):
        self.registry.register(self.filter)
        self.assertEqual(self.registry.size, 1)

    def test_register_with_iterable(self):
        self.registry.register([self.filter])
        self.assertEqual(self.registry.size, 1)
                
    def test_register_non_filter_raises_unregisterable(self):
        with self.assertRaises(Unregisterable):
            self.registry.register(self.non_filter)

    def test_register_on_duplicate_key_raises_alreadyRegistered(self):
        self.registry.register(self.filter)
        with self.assertRaises(AlreadyRegistered):
            self.registry.register(self.filter)

    def test_call(self):
        self.registry.register(self.filter)
        r = self.registry(self.filter.human_id())
        self.assertTrue(isinstance(r, Thumb))        

    def test_register_call_missing_key_raises_notregistered(self):
        with self.assertRaises(NotRegistered):
            self.registry('stuff_n_nuff')
                            
    def test_unregister(self):
        self.registry.register(self.filter)
        self.registry.unregister(self.filter)
        self.assertEqual(self.registry.size, 0)


from image.settings import settings

class TestSettings(TestCase):
    # it does a lot of checking itself. Without going overboard,
    # initialisation is all that needs checking.
    def setUp(self):
        self.settings = settings
        
        
from image import decisions
class TestDecisions(TestCase):
    def setUp(self):
        self.decisions = decisions

    def test_long_imagename_truncated(self):
        filepath = '/home/nightmare/originals/Cetron-DKZ800-Carphones-FurryDice-for-BMW-iPad-Fridge-Solidus-Nokirapo-MP3-players-etc-WITHOUT-Microphone-and-remote-0-2-uai-258x258.tiff'
        r = self.decisions.image_save_path(filepath)
        self.assertLessEqual(len(r), 100) 

    def test_long_reformname_truncated(self):
        filepath = '/home/nightmare/originals/Cetron-DKZ800-Carphones-FurryDice-for-BMW-iPad-Fridge-Solidus-Nokirapo-MP3-players-etc-WITHOUT-Microphone-and-remote-0-2-uai-258x258-twas-a-filter-name.bake.png.tiff'
        r = self.decisions.reform_save_path(filepath)
        self.assertLessEqual(len(r), 100)         

        
class TestReforms(TestCase):
    def setUp(self):
        self.image = Image.objects.create(
            title="Test image",
            src=get_test_image_file_jpg(),
        )
        self.filter = Thumb()
        self.reform = self.image.get_reform(self.filter)

    def test_filter_id(self):
        # check that the id returned from the reform is the filter id,
        self.assertEqual(self.reform.filter_id, Thumb.human_id())

    # # Can't. It's only a FileField.
    # # def test_resize(self):
        # # # Check size
        # # self.assertEqual(self.reform.src.width, 64)
        # # self.assertEqual(self.reform.src.height, 64)
        
    def test_src_name(self):
        self.assertEqual(self.reform.src.name, "reforms/test-image_thumb.png")
        
    def test_url_attribute(self):
        self.assertEqual(self.reform.url, "/media/reforms/test-image_thumb.png")
        
    def test_alt_attribute(self):
        self.assertEqual(self.reform.alt, "Test image")

    def tearDown(self):    
        self.reform.src.delete(False)
        self.image.src.delete(False)
