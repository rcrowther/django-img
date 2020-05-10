import os
from pathlib import Path

from django.core.exceptions import ValidationError
from django.forms.fields import ImageField
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _
from image.constants import IMAGE_FORMATS, ALLOWED_FILE_EXTENSIONS
from image import settings


class ImgField(ImageField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get max upload size from settings
        self.max_upload_size = settings.max_upload_size * 10 * 1024 * 1024
        max_upload_size_text = filesizeformat(self.max_upload_size)
        supported_formats_text = ", ".join(IMAGE_FORMATS)

        # Help texts
        if self.max_upload_size is not None:
            self.help_text = "Supported formats: {}. Maximum filesize: {}.".format(
                supported_formats_text,
                max_upload_size_text,
            )
        else:
            self.help_text = "Supported formats: {}.".format(
                supported_formats_text
            )

        # Error messages
        self.error_messages['invalid_image'] = "Not a supported image format. Supported formats: {}.".format(
            supported_formats_text
            )

        self.error_messages['invalid_image_known_format'] = "Not a valid {} image."

        self.error_messages['file_too_large'] = _(
            "This file is too big ({{}}). Maximum filesize {}.".format(
                max_upload_size_text
            )

        self.error_messages['file_too_large_unknown_size'] = "This file is too big. Maximum filesize {}.".format(
            max_upload_size_text
        )
        
    def check_image_file_format(self, f):
        # Check file extension
        fp = Path(f.name)
        extension = fp.extension
        if extension not in ALLOWED_FILE_EXTENSIONS:
            raise ValidationError(self.error_messages['invalid_image'], code='invalid_image')

        image_format = extension.upper()
        if image_format == 'JPG':
            image_format = 'JPEG'

        guessed_image_format = f.image.format.upper()
        if guessed_image_format == 'MPO':
            guessed_image_format = 'JPEG'

        # Check the internal format matches the extension
        if guessed_image_format != image_format:
            raise ValidationError(self.error_messages['invalid_image_known_format'].format(
                image_format
            ), code='invalid_image_known_format')

    def check_image_file_size(self, f):
        # Don't try if no max upload size declared
        if self.max_upload_size is None:
            return

        # Check filesize
        if f.size > self.max_upload_size:
            ???
            raise ValidationError(self.error_messages['file_too_large'].format(
                filesizeformat(f.size),
            ), code='file_too_large')

    def to_python(self, data):
        f = super().to_python(data)

        if f is not None:
            self.check_image_file_size(f)
            self.check_image_file_format(f)

        return f
