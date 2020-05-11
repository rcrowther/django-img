from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import filesizeformat

from image import settings
from image.constants import IMAGE_FORMATS, ALLOWED_FILE_EXTENSIONS


# Yes, I know this exists - FileExtensionValidator
def validate_image_file_extension(file):
        fp = Path(file.name)
        extension = fp.extension
        if extension not in ALLOWED_FILE_EXTENSIONS:
            raise ValidationError(
                "Not a supported image format. Supported formats: {}.".format(
                    ", ".join(IMAGE_FORMATS)
                ))

        image_format = extension.upper()
        if image_format == 'JPG':
            image_format = 'JPEG'

        guessed_image_format = file.image.format.upper()
        if guessed_image_format == 'MPO':
            guessed_image_format = 'JPEG'

        # Check the internal format matches the extension
        if (guessed_image_format != image_format):
            raise ValidationError(
                "Not a valid {} image.".format(
                    image_format
                ))
            

def validate_file_size(file):
       # Don't try if no max upload size declared
        if (settings.max_upload_size is None):
            return

        # Check filesize
        if (file.size > settings.max_upload_size):
            raise ValidationError(
                "This file is too big* ({}). Maximum filesize {}.".format(
                    filesizeformat(file.size),
                    filesizeformat(settings.max_upload_size)
                ))
