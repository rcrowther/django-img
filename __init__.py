#from image.decorators import register

from image.filters import (
    Format, Resize, Crop, ResizeSmart, Thumb
)

__all__ = [
    "Format", "Resize", "Crop", "ResizeSmart", "Thumb",
    ]
# See django.contrib.admin.__init__()
#def autodiscover():
#    autodiscover_modules('admin', register_to=site)


#default_app_config = 'django.contrib.admin.apps.AdminConfig'
