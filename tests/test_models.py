import unittest

from django.test import TestCase
from image.models import Image, Reform, SourceImageIOError
from .utils import Image, get_test_image_file


# ./manage.py test image.tests
class TestImage(TestCase):
    def setUp(self):
        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            src=get_test_image_file(),
        )
        
    def test_is_portrait(self):
        self.assertFalse(self.image.is_portrait())

    def test_is_landscape(self):
        self.assertTrue(self.image.is_landscape())
        
    def test_is_stored_locally(self):
        self.assertTrue(self.image.is_stored_locally())
        
    def test_bytesize_on_missing_file_raises_sourceimageioerror(self):
        self.image.src.delete(save=False)
        with self.assertRaises(SourceImageIOError):
            self.image.bytesize


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
    Unregisterable, 
    AlreadyRegistered, 
    NotRegistered
)

#from image.filters_pillow import Crop, ResizeSmart

class NonFilter():
    pass
    
class TestClassRegistry(TestCase):
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
        # assert return is instance of filter?
        self.assertTrue(isinstance(r, Thumb))        
                
    def test_unregister(self):
        self.registry.register(self.filter)
        self.registry.unregister(self.filter)
        self.assertEqual(self.registry.size, 0)

    # # def test_filename(self):
        # # self.registry.module_path(klass)
                        
# class TestReforms(TestCase):
    # def setUp(self):
        # # Create an image for running tests on
        # self.image = Image.objects.create(
            # title="Test image",
            # src=get_test_image_file(),
        # )

        # self.filter = registry('image.Thumb')
        
    # #def test_get_rendition_model(self):
    # #    self.assertIs(Image.get_rendition_model(), Rendition)

    # def test_creation(self):
        # reform = self.image.get_reform(self.filter)

        # # Check size
        # self.assertEqual(reform.src.width, 64)
        # self.assertEqual(reform.src.height, 64)

        # # check that the rendition has been recorded under the correct filter,
        # # via the Rendition.filter_spec attribute (in active use as of Wagtail 1.8)
        # self.assertEqual(reform.filter_id, 'image.image_filters.Thumb')

    # # def test_resize_to_max(self):
        # # rendition = self.image.get_rendition('max-100x100')

        # # # Check size
        # # self.assertEqual(rendition.width, 100)
        # # self.assertEqual(rendition.height, 75)

    # # def test_resize_to_min(self):
        # # rendition = self.image.get_rendition('min-120x120')

        # # # Check size
        # # self.assertEqual(rendition.width, 160)
        # # self.assertEqual(rendition.height, 120)

    # # def test_resize_to_original(self):
        # # rendition = self.image.get_rendition('original')

        # # # Check size
        # # self.assertEqual(rendition.width, 640)
        # # self.assertEqual(rendition.height, 480)

    # # def test_cache(self):
        # # # Get two renditions with the same filter
        # # first_rendition = self.image.get_rendition('width-400')
        # # second_rendition = self.image.get_rendition('width-400')

        # # # Check that they are the same object
        # # self.assertEqual(first_rendition, second_rendition)

    # def test_alt_attribute(self):
        # reform = self.image.get_reform(self.filter)
        # self.assertEqual(reform.alt, "Test image")
