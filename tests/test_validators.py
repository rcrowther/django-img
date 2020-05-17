from django.test import TestCase

from django.db.models.fields.files import ImageFieldFile
from django.core.files.base import File
from django.core.files.storage import Storage, default_storage
from django.core.exceptions import ValidationError

from image.validators import (
    validate_image_file_extension,
    validate_file_size
)
from image import settings

from .utils import get_test_image_file_jpg



# Tests the class for attributes and checks, not the action.
class TestValidators(TestCase):
    def setUp(self):
        fakefield = lambda: None
        fakefield.storage = default_storage
        self.file = ImageFieldFile(instance=None, field=fakefield, name='test.jpg')
        self.file.file = get_test_image_file_jpg()

    def test_file_extension(self):
        validate_image_file_extension(self.file)

    def test_unrecognisable_file_extension_raises_validationerror(self):
        self.file.name = 'test#ogg'
        with self.assertRaises(ValidationError):
            validate_image_file_extension(self.file)
        
    def test_unrecognised_file_extension_raises_validationerror(self):
        self.file.name = 'test.ogg'
        with self.assertRaises(ValidationError):
            validate_image_file_extension(self.file)

    def test_unmatched_file_extension_raises_validationerror(self):
        self.file.name = 'test.tiff'
        with self.assertRaises(ValidationError):
            validate_image_file_extension(self.file)

    # next two tests are heavily mocked,
    # but will show up code bugs
    def test_file_size(self):
        # Coax the Django file into thinking it has a size
        # (triggering size() code will return an error)
        self.file._committed = False
        self.file.file.size = 1500000
        validate_file_size(self.file)

    def test_excessive_file_sizen_raises_validationerror(self):
        # preset 2M for settings
        settings._max_upload_size = 2
        # fake up a 20M file
        fakefile = lambda: None
        fakefile.size = 20000000
        with self.assertRaises(ValidationError):
            validate_file_size(fakefile)
