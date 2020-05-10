import os
from functools import lru_cache

from django.core.checks import Warning, register
from PIL import Image as PILImage


@lru_cache()
def has_jpeg_support():
    test_jpg = os.path.join(os.path.dirname(__file__), 'check_files', 'test.jpg')
    succeeded = True

    with open(test_jpg, 'rb') as f:
        try:
            PILImage.open(f)
        except (IOError, PILImage.LoaderError):
            succeeded = False

    return succeeded


@lru_cache()
def has_png_support():
    test_png = os.path.join(os.path.dirname(__file__), 'check_files', 'test.png')
    succeeded = True

    with open(test_png, 'rb') as f:
        try:
            PILImage.open(f)
        except (IOError, Image.LoaderError):
            succeeded = False

    return succeeded


@register()
def image_library_check(app_configs, **kwargs):
    errors = []

    if not has_jpeg_support():
        errors.append(
            Warning(
                'JPEG image support is not available',
                hint="Check that the 'libjpeg' library is installed, then reinstall Pillow."
            )
        )

    if not has_png_support():
        errors.append(
            Warning(
                'PNG image support is not available',
                hint="Check that the 'zlib' library is installed, then reinstall Pillow."
            )
        )

    return errors
