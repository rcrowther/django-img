from wagtail.images.models import SourceImageIOError


def get_reform_or_not_found(image, specs):
    """
    Tries to get / create the reform for the image or renders a not-found image if it does not exist.
    :param image: AbstractImage
    :param specs: str or Filter
    :return: Reform
    """
    try:
        return image.get_reform(specs)
    except SourceImageIOError:
        # Image file is (probably) missing from /media/original_images - generate a dummy
        # reform so that we just output a broken image, rather than crashing out completely
        # during rendering.
        Reform = image.reforms.model  # pick up any custom Image / Reform classes that may be in use
        reform = Reform(image=image, width=0, height=0)
        reform.file.name = 'not-found'
        return reform
