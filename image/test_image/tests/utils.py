import os
from io import BytesIO
import PIL.Image
from django.core.files.images import ImageFile

from test_image.models import TestImage
from image.image_filters import Thumb
#from .image_subclass import NewsArticleImage, NewsArticleReform

        
def get_test_image_file_png(filename='test.png', colour='white', size=(640, 480)):
    '''
    Return a generated png image as a Django ImageFile.
    The image is loaded in a bytebuffer, not on disc.
    '''
    f = BytesIO()
    image = PIL.Image.new('RGBA', size, colour)
    image.save(f, 'PNG')
    return ImageFile(f, name=filename)


def get_test_image_file_jpg(filename='test.jpg', colour='white', size=(640, 480)):
    '''
    Return a generated jpg image as a Django ImageFile.
    The image is loaded in a bytebuffer, not on disc.
    '''
    f = BytesIO()
    image = PIL.Image.new('RGB', size, colour)
    image.save(f, 'JPEG')
    return ImageFile(f, name=filename)


def get_test_image_file_webp(filename='test.webp', colour='white', size=(640, 480)):
    '''
    Return a generated webp image as a Django ImageFile.
    The image is loaded in a bytebuffer, not on disc.
    '''
    f = BytesIO()
    image = PIL.Image.new('RGB', size, colour)
    image.save(f, 'WEBP')
    return ImageFile(f, name=filename)


def get_test_image():
    '''
    Generate an image in the db.
    '''
    im = TestImage.objects.create(
            src=get_test_image_file_jpg(),
        )
    return im

def image_delete(image):
    '''
    Remove an image
    Due to basic settings and test transaction handling, a test will not
    remove an image without leaving files.
    '''
    os.remove(image.src.path)
    image.delete(False)
        
def get_test_reform():
    '''
    Generate an image and reform in the db.
    '''
    im = get_test_image()
    return im.get_reform(Thumb())

def reform_delete(reform):
    '''
    Remove a reform
    Due to basic settings and test transaction handling, a test will not
    remove an image without leaving files.
    '''
    os.remove(reform.src.path)
    image_delete(reform.image)
    
# Seems to work but not on foreign keys
# So Django documentation wants to lecture me about testing. How about 
# some gear for subclassing? Because so far I've found nothing that 
# works. R.C.
from django.db import connection
    
#from django.db import connection
#from django.db.migrations.loader import MigrationLoader
#        loader = MigrationLoader(connection)
# from django.core.management import call_command

def create_subclass():
    # needs to install the app
    #call_command('mkmigrations', 'image.tests.test_image_subclass')
    #call_command('migrate', 'image.tests.test_app')

#! SQLite schema editor cannot be used while foreign key constraint checks are enabled.
#? but how?
# https://stackoverflow.com/questions/7020966/how-to-create-table-during-django-tests-with-managed-false
#
    print('test create subclass')
    #with connection.schema_editor() as schema_editor:
    #    pass
        #schema_editor.create_model(NewsArticleImage)
        #schema_editor.create_model(NewsArticleReform)

        # if NewsArticleImage._meta.db_table not in connection.introspection.table_names():
            # raise ValueError("Table `{table_name}` is missing in test database.".format(
                # table_name=NewsArticleImage._meta.db_table
            # ))  


#def get_subclass_image():
#    im = NewsArticleImage.objects.create(
#            src=get_test_image_file_jpg(),
#        )
#    return im
