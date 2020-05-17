from io import BytesIO
import PIL.Image
from django.core.files.images import ImageFile

from image.models import Image

def get_test_image_file_png(filename='test.png', colour='white', size=(640, 480)):
    f = BytesIO()
    image = PIL.Image.new('RGBA', size, colour)
    image.save(f, 'PNG')
    return ImageFile(f, name=filename)


def get_test_image_file_jpg(filename='test.jpg', colour='white', size=(640, 480)):
    f = BytesIO()
    image = PIL.Image.new('RGB', size, colour)
    image.save(f, 'JPEG')
    return ImageFile(f, name=filename)


def get_test_image_file_webp(filename='test.webp', colour='white', size=(640, 480)):
    f = BytesIO()
    image = PIL.Image.new('RGB', size, colour)
    image.save(f, 'WEBP')
    return ImageFile(f, name=filename)
