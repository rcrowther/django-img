from image.models import SourceImageIOError
import os.path
from django.templatetags.static import static
from django.core.files.images import ImageFile
from django.core.files.storage import FileSystemStorage
from image.utils import url_absolute_static_aware
from image import settings

#? cache
def image_broken_url():
    '''
    Deliver a static-aware 'broken url' path.
    '''
    return  url_absolute_static_aware(settings.broken_image_path)
     
def get_reform_or_not_found(image, ifilter):
    """
    Tries to get / create the reform for the image or renders a 
    not-found image if it does not exist.
    :param image: AbstractImage instance
    :param filter_id: str or Filter
    :return: Reform
    """
    try:
        return image.get_reform(ifilter)
    except SourceImageIOError:
        print('short cut')
        # (probably) SourceImageIOError indicates an Image is missing 
        # it's file. Instead of throwing a page error, make a mock
        # reform to hold a generic broken image.
        #? is this expensive?
        Reform = image.get_reform_model()
        fp = image_broken_url()
        reform = Reform(
            image=image, 
            filter_id=ifilter.human_id()
        )

        # A textlike src.name triggers no attempt to 'upload'.
        reform.src.name = image_broken_url()
        
        # To make a new URL work, needs a rerouted storage
        # (default points at /media)
        reform.src.storage = FileSystemStorage(base_url='/')
        return reform
