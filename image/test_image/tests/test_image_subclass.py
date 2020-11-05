import unittest

from django.test import TestCase
from .utils import (
    create_subclass,
)


# ./manage.py test image.tests.test_image_subclass
#! NOT WORKING
class TestImageSubclass(TestCase):
    '''
    Base tests avoid reform creation, object deletion, subclassing
    '''
    #def init(self):
    #    super().__init__()
    #    create_subclass()
        
    #def setUp(self):
     #   create_subclass()
        #self.image = get_subclass_image()

    def test_upload_dir(self):
        create_subclass()
    #    self.assertEqual(self.image.upload_dir, 'originals')

    # def test_filepath_length(self):
        # self.assertEqual(self.image.filepath_length, 100)

    # def test_path_checks(self):
        # self.image.__class__.filepath_length = -300
        # errors = self.image.check()
        # self.assertEqual(errors[0].id, 'image_model.E001')
        
    # def test_upload_time(self):
        # self.assertNotEqual(self.image.upload_time, None)
        
    # def test_src_name(self):
        # self.assertEqual(self.image.src.name, 'originals/test.jpg')

    # def test_width(self):
        # self.assertEqual(self.image.width, 640)

    # def test_height(self):
        # self.assertEqual(self.image.height, 480)
                
    # def test_bytesize(self):
        # size = self.image.bytesize
        # self.assertIsInstance(size, int)
        # self.assertGreater(size, 0)
        
    # def test_bytesize_on_missing_file_raises_sourceimageioerror(self):
        # self.image.src.delete(save=False)
        # with self.assertRaises(SourceImageIOError):
            # self.image.bytesize

    # def test_is_local(self):
        # self.assertTrue(self.image.is_local())

    # def test_filename(self):
        # self.assertEqual(self.image.filename, 'test.jpg')
                    
    # def test_alt(self):
        # self.assertEqual(self.image.alt, 'test image')
                        
    # def test_is_portrait(self):
        # self.assertFalse(self.image.is_portrait())

    # def test_is_landscape(self):
        # self.assertTrue(self.image.is_landscape())
        
    # def tearDown(self):
        # self.image.src.delete(False) 
