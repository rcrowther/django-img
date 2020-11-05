import unittest

from django.test import TestCase
from image.models import SourceImageIOError
from . import utils


# A fundamental issue throughout the tests is that image uploading 
# is transactional. But TestCase will not complete over transactions
# So fails to trigger file deletion. 
# Rather than using TestTransaction, which is less clean, these tests 
# are littered with rearDown() methods to clean up orphaned files 
# (poor orphans, unwanted...). 
# ./manage.py test image.tests.test_image
class TestImage(TestCase):
    '''
    Base tests avoid reform creation, object deletion, subclassing
    '''
    def setUp(self):
        self.image = utils.get_test_image()

    def test_upload_dir(self):
        self.assertEqual(self.image.upload_dir, 'test_originals')

    def test_filepath_length(self):
        self.assertEqual(self.image.filepath_length, 55)

    def test_path_checks(self):
        self.image.__class__.filepath_length = -300
        errors = self.image.check()
        self.assertEqual(errors[0].id, 'testimage.E003')
        
    def test_upload_time(self):
        self.assertNotEqual(self.image.upload_time, None)
        
    def test_src_name(self):
        self.assertEqual(self.image.src.name, 'test_originals/test.jpg')

    def test_width(self):
        self.assertEqual(self.image.width, 640)

    def test_height(self):
        self.assertEqual(self.image.height, 480)
                
    def test_bytesize(self):
        size = self.image.bytesize
        self.assertIsInstance(size, int)
        self.assertGreater(size, 0)
       
    #?
    # def test_bytesize_on_missing_file_raises_sourceimageioerror(self):
        # image = utils.get_test_image()
        # utils.image_delete(image)
        # with self.assertRaises(SourceImageIOError):
            # image.bytesize

    def test_is_local(self):
        self.assertTrue(self.image.is_local())

    def test_filename(self):
        self.assertEqual(self.image.filename, 'test.jpg')
                    
    def test_alt(self):
        self.assertEqual(self.image.alt, 'test image')
                        
    def test_is_portrait(self):
        self.assertFalse(self.image.is_portrait())

    def test_is_landscape(self):
        self.assertTrue(self.image.is_landscape())
        
    def tearDown(self):
        utils.image_delete(self.image)
