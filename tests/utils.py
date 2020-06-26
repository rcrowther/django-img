from io import BytesIO
import PIL.Image
from django.core.files.images import ImageFile

from image.models import Image
from image.image_filters import Thumb
from .image_subclass import NewsArticleImage, NewsArticleReform

    
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

def get_test_image():
    im = Image.objects.create(
            src=get_test_image_file_jpg(),
        )
    return im
    
def get_test_reform():
    im = get_test_image()
    return im.get_reform(Thumb())

# seems to work but not on foreign keys
from django.db import connection
def get_image_subclass():
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(NewsArticleImage)

        if NewsArticleImage._meta.db_table not in connection.introspection.table_names():
            raise ValueError("Table `{table_name}` is missing in test database.".format(
                table_name=NewsArticleImage._meta.db_table
            ))

    im = NewsArticleImage.objects.create(
            src=get_test_image_file_jpg(),
        )
        
    return im
