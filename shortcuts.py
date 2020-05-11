from image.models import SourceImageIOError
import os.path

# cache
def image_broken_filepath():
    return os.path.join(os.path.dirname(__file__), 'files', 'notfound.png')
 
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
        # Image file is (probably) missing from /media/original_images - generate a dummy
        # reform so that we just output a broken image, rather than crashing out completely
        # during rendering.
        # pick up any custom Image / Reform classes that may be in use
        Reform = image.reforms.model  
        reform = Reform(image=image)
        reform.src.name = image_broken_filepath()
        return reform
