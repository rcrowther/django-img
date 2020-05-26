from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.forms import Media
from django.utils.html import format_html
from django import forms
from django.db import models
                         
from image.models import Image, Reform
from image import widgets

from image.admins import ImageLockedAdmin
                          
                                    
                                    
class ImageAdmin(ImageLockedAdmin):
#class ImageAdmin(admin.ModelAdmin):
    pass
          
admin.site.register(Image, ImageAdmin)
