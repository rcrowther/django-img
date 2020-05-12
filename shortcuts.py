from image.models import Reform, SourceImageIOError
import os.path

# cache
def image_broken_filepath():
    return os.path.join(os.path.dirname(__file__), 'files', 'unfound.png')
 
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
        # (probably) Image file is missing from /media images. So
        # make a mock reform to hold a generic broken image, rather than
        # crashing out completely.
        # A text filepath parameter triggers no attempt to 'upload'.
        Reform = image.reforms.model  
        reform = Reform(image=image)
        reform.src.name = image_broken_filepath()
        return reform
