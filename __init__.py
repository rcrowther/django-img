#from image.decorators import register

from image.filters import (
    FormatFilter, ResizeFilter, CropFilter, ResizeSmartFilter, Thumb
)

__all__ = [
    "FormatFilter", "ResizeFilter", "CropFilter", "ResizeSmartFilter", "Thumb",
    ]
# See django.contrib.admin.__init__()
#def autodiscover():
#    autodiscover_modules('admin', register_to=site)


#default_app_config = 'django.contrib.admin.apps.AdminConfig'
