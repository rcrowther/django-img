#from image.decorators import register
from image.registry import registry
from image import utils

from image.filters import (
    Filter, Format, Resize, Crop, ResizeSmart, Thumb
)

__all__ = [
    "Format", "Resize", "Crop", "ResizeSmart", "Thumb",
    "register", "registry", "autodiscover"
    ]


settings = utils.Settings()


# becaue autodiscover_noncore_modules does a hairy import, which will 
# fail on Django initialisation, it is run from ImageConfig in apps.py
def autodiscover():
    utils.autodiscover(
        'image_filters', 
        parents=settings.modules, 
        find_in_apps=True, 
        not_core_apps=True
        )

# @functools.lru_cache(maxsize=None)
# def get_filters():

