from django.contrib import admin
from image.models import Image, Reform


class ImageAdmin(admin.ModelAdmin):
    pass
#    fields = ('mdl', 'make', 'img')
#    exclude = ('awds')

    # formfield_overrides = {
        # ImageField: {'widget': AdminImageChooser},
        # ImgField: {'widget': AdminImageChooser},
    # }
    
admin.site.register(Image, ImageAdmin)


class ReformAdmin(admin.ModelAdmin):
    pass
#    fields = ('mdl', 'make', 'img')
#    exclude = ('awds')

    # formfield_overrides = {
        # ImageField: {'widget': AdminImageChooser},
        # ImgField: {'widget': AdminImageChooser},
    # }
    
admin.site.register(Reform, ReformAdmin)
