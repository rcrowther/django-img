from image.models import Reform, SourceImageIOError
import os.path
from django.templatetags.static import static
from django.core.files.images import ImageFile
from django.core.files.storage import FileSystemStorage


#? cache
def image_broken_url():
    '''
    Deliver a static-aware 'broken url' path.
    '''
    # keeps returning media/static...
    #return static('image/unfound.png')
    return 'unfound.png'
     
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
        # it's file. Instead of throwing a whole page error, make a mock
        # reform to hold a generic broken image.
        # A textlike parameter triggers no attempt to 'upload'.
        # Also note the path is relative to the site.
        #! is this expensive?
        fp = image_broken_url()
        reform = Reform(
            image=image, 
            filter_id=ifilter.human_id()
        )
        reform.src.name = 'static/image/unfound2.png'
        
        #? To make a new URL work, needs a rerouted storage
        # (default points at /media)
        reform.src.storage = FileSystemStorage(base_url='/')
        return reform
