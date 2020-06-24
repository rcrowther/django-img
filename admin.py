from django.contrib import admin
                         
from image.admins import ImageCoreAdmin
from image.models import Image, Reform
          
                          
                                    
# Custom admin interface for administering an Image collection.
class ImageAdmin(ImageCoreAdmin):
    
# Stock admin interface.
#class ImageAdmin(admin.ModelAdmin):
    pass
        
        
admin.site.register(Image, ImageAdmin)
