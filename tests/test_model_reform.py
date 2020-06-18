import unittest

from django.test import TestCase
from image.models import Image, Reform, SourceImageIOError
from image.image_filters import Thumb
from .utils import get_test_image_file_jpg



# ./manage.py test image.tests.test_model_reform
class TestReforms(TestCase):
    '''
    Base tests avoid object deletion and subclassing
    '''
    def setUp(self):
        self.image = Image.objects.create(
            src=get_test_image_file_jpg(),
            auto_delete=Image.AutoDelete.YES,
        )
        self.filter = Thumb()
        self.reform = self.image.get_reform(self.filter)

    def test_upload_to_dir(self):
        self.assertEqual(self.reform.upload_to_dir, 'reforms')

    def test_filepath_length(self):
        self.assertEqual(self.reform.filepath_length, 100)

    # def test_path_checks(self):
        # self.reform.__class__.filepath_length = -300
        # errors = self.image.check()
        # self.assertEqual(errors[0].id, 'image_model.E001')
        

    # # Can't. It's only a FileField.
    # # def test_resize(self):
        # # # Check size
        # # self.assertEqual(self.reform.src.width, 64)
        # # self.assertEqual(self.reform.src.height, 64)
        
    def test_src_name(self):
        self.assertEqual(self.reform.src.name, "reforms/test-image_thumb.png")

    def test_filter_id(self):
        self.assertEqual(self.reform.filter_id, Thumb.human_id())
        
    def test_url(self):
        self.assertEqual(self.reform.url, "/media/reforms/test-image_thumb.png")
        
    def test_alt(self):
        self.assertEqual(self.reform.alt, "test image")

    def tearDown(self):    
        self.reform.src.delete(False)
        self.image.src.delete(False)
