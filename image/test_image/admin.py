from django.contrib import admin
                         
from image.admins import ImageCoreAdmin
from test_image.models import TestImage                 
                                    
# Custom admin interface for administering an Image collection.
class TestImageImageAdmin(ImageCoreAdmin):
    pass
        
        
admin.site.register(TestImage, TestImageImageAdmin)
