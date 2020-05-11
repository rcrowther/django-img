#from image.decorators import register
from  image.settings import settings
from image.registry import registry #, register
from image import utils

print('create __init__')


# from image.filters_pillow import (
    # #Filter, 
    # Format, Resize, Crop, ResizeSmart, CropSmart
# )

__all__ = [
    # "Format", "Resize", "Crop", "ResizeSmart", "CropSmart",
    #"Thumb",
    #"register", "registry", "autodiscover"
    ]


# becaue autodiscover_noncore_modules does a hairy import, which will 
# fail on Django initialisation, it is run from ImageConfig in apps.py
def autodiscover():
    utils.autodiscover(
        'image_filters', 
        parents = settings.modules, 
        find_in_apps = settings.app_dirs, 
        not_core_apps = True
    )
