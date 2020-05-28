import unittest

from django.test import TestCase
from image.models import Image, Reform, SourceImageIOError
from .utils import get_test_image_file_jpg


# A fundamental issue throughout the tests is that image uploading 
# shunts files about. But TestCase will not complete over transactions
# So fails to trigger file deletion. So these tests are littered
# with rearDown() methods to clean up orphaned test files (poor orphans,
# unwanted...). 
# ./manage.py test image.tests.test_models
class TestImage(TestCase):
    def setUp(self):
        self.image = Image.objects.create(
            title="Test",
            src=get_test_image_file_jpg(),
            auto_delete=Image.AutoDelete.YES,
        )

    def test_src_name(self):
        self.assertEqual(self.image.src.name, 'originals/test.jpg')

    def test_alt(self):
        self.assertEqual(self.image.alt, 'test image')
                        
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



from image.image_filters import Thumb

class TestReforms(TestCase):
    def setUp(self):
        self.image = Image.objects.create(
            title="Test",
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
        self.assertEqual(self.reform.alt, "test image")

    def tearDown(self):    
        self.reform.src.delete(False)
        self.image.src.delete(False)
