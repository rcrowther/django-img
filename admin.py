from django.contrib import admin
from image.models import Image, Reform


class ImageAdmin(admin.ModelAdmin):
    fields = ('title', 'image', 'bytesize')
    
admin.site.register(Image, ImageAdmin)
