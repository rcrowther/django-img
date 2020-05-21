from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.forms import Media
from django.utils.html import format_html
from django import forms
from django.db import models
                         
from image.models import Image, Reform
from image import widgets


                          
                                    
class ImageAdmin(admin.ModelAdmin):
    # For pooled files, replace the above with this
    #fields = ('title', 'src', 'auto_delete')
    #readonly_fields = ('src',)

    # case-insensitive contains match
    search_fields = ['title']
    #! how about delete button?
    list_display = ('title', 'upload_day', 'view_image')
    #list_display = ('title', 'upload_day')
    #prepopulated_fields = {"title": ("src",)}

    def __init__(self, model, admin_site):
        # Consistent API here, please. I'd use a set, but Python tells
        # me that's unhashable.
        self.readonly_fields = list(self.readonly_fields)
        super().__init__(model, admin_site)
        

    def view_image(self, obj):
        # Can't say I like Django styling, but 'button' is what I can 
        # find as given.
        return format_html('<a href="{}" class="button">View</span></a>',
            obj.src.url
        )
    view_image.short_description = 'View Image'

    def upload_day(self, obj):
        '''e.g.	17 May 2020'''
        return format_html('{}',
            obj.upload_date.strftime("%d %b %Y")
        )
    upload_day.short_description = 'Upload day'
    upload_day.admin_order_field = 'upload_date'


    formfield_overrides = {
        # This changes the 'change' form to not display the view link
        #models.ImageField: {'widget': forms.FileInput},
        #models.ImageField: {'widget': widgets.FileSingleChooserDAndD},
        
        #forms.ImageField: {'widget': admin.widgets.AdminFileWidget},
    }
    
    def get_form(self, request, obj=None, change=False, **kwargs):
        # Only way I can think of differentiating between the two forms.
        # change attribute behaves so inconsistently I think I have an
        # API problem, and documentation doesn't match. But object
        # detection works.
        # This must be defensive code, because it's a class-wide 
        # attribute. Again, I don't currently see a way in aside from
        # tearing the element foo and on, like Javascript.
        if (obj):
            if (not('src'in self.readonly_fields)): 
                self.readonly_fields.append('src')
        else:
            if ('src'in self.readonly_fields): 
                self.readonly_fields.remove('src')
        return super().get_form( request, obj, change, **kwargs)
        
    @property
    def media(self):
        base = super().media
        for jslist in base._js_lists:
            for i, e in enumerate(jslist): 
                if e == 'admin/js/prepopulate.js':
                    jslist[i] = 'image/js/prepopulate.js'
        return base
         
admin.site.register(Image, ImageAdmin)
