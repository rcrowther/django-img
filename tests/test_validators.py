from django.test import TestCase

from django.core.exceptions import ValidationError

from image.validators import (
    validate_image_file_extension,
    validate_file_size,
)

from .utils import get_test_image_file_jpg, get_test_image


# ./manage.py test image.tests.test_validators
#! ought to test in place on an Image, if not as request
class TestValidators(TestCase):
    def setUp(self):
        self.file = get_test_image_file_jpg()
        
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
        self.file.file.size = 750000
        validate_file_size(1000000, self.file)

    def test_excessive_file_sizen_raises_validationerror(self):
        # Coax the Django file into thinking it has a size
        # (triggering size() code will return an error)
        self.file._committed = False
        self.file.file.size = 2000000
        with self.assertRaises(ValidationError):
            validate_file_size(1000000, self.file)

