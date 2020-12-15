"""Image handling for Django. Includes upload code, repository and filter creation. Low on features, fast setup, modular."""
__version__ = '0.1.5'

from image.decorators import register
from image.filters import Filter
from image.filters_pillow import (
    Format, Resize, Crop, ResizeSmart, CropSmart
)
from image.settings import settings
from image.registry import registry
from image.module_loading import autodiscover_modules

__all__ = [
    "register"
    "Filter",
    "Format", "Resize", "Crop", "ResizeSmart", "CropSmart",
    "Thumb",
    "registry",
    ]


# autodiscover_modules does a hairy import, which will 
# fail on Django initialisation, so is run from ImageConfig in apps.py
def autodiscover():
    autodiscover_modules(
        'image_filters', 
        parent_modules = settings.modules, 
        find_in_apps = settings.app_dirs, 
        not_core_apps = True
    )
