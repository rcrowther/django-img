from django.contrib import admin
#from django.utils.translation import gettext_lazy as _
from django.forms import Media
from django.utils.html import format_html
from django import forms
from django.db.models import ImageField
                         
#from image.models import Image, Reform
from image.widgets import FileChooserDAndD


                                    
class ImageLockedAdmin(admin.ModelAdmin):
    # locks files to images by disallowing editing. 
    # Includes several other Admin configurations and hacks.
    
    #! All the below can be commented or adapted to remove/change 
    # particular effects.
    # See the notes.
    
    # case-insensitive contains match
    search_fields = ['title']
    
    # Style the lists.
    # See the support code below
    #! how about delete button?
    list_display = ('title', 'upload_day', 'view_image')

    # Enhance file pickers, sometimes, with a drop area. 
    # See note on Media.
    #! throws a dependency error on change files
    #prepopulated_fields = {"title": ("src",)}

    def __init__(self, model, admin_site):
        # Consistent API here, please. I'd use a set, but Python tells
        # me that's unhashable.
        # Needed for the upload locking.
        self.readonly_fields = list(self.readonly_fields)
        super().__init__(model, admin_site)
        
    # Support code for styling the admin list
    # See the 'list_display' attribute.
    def view_image(self, obj):
        # Can't say I like Django styling, but 'button' is what I find 
        # as given.
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

    # Choose a style of upload pickers
    formfield_overrides = {
        # Basic django browse button.
        #ImageField: {'widget': forms.FileInput},
        
        # Admin picker enhanced with current file display. Admin 
        # default. Some don't like it, some do.
        #ImageField: {'widget': admin.widgets.AdminFileWidget},
        
        # Image picker has a simple drop field
        ImageField: {'widget': FileChooserDAndD},
    }
    
    # Block filechoosing on uploaded Image models.
    def get_form(self, request, obj=None, change=False, **kwargs):
        # This must be defensive code, because readonly is a class-wide 
        # attribute. I don't currently see a way in aside from
        # push/popping the readonly attribute, like Javascript.
        #
        # Only way I can think of differentiating between the two forms.
        # change attribute behaves inconsistently---think I have an
        # API problem, and documentation doesn't match. But object
        # detection works.
        if (obj):
            if (not('src'in self.readonly_fields)): 
                self.readonly_fields.append('src')
        else:
            if ('src'in self.readonly_fields): 
                self.readonly_fields.remove('src')
        return super().get_form( request, obj, change, **kwargs)
        
    # Code for prepopulation, with special handling of 
    # SingleImageFields. See 'prepopulate' attribute.
    @property
    def media(self):
        base = super().media
        for jslist in base._js_lists:
            for i, e in enumerate(jslist): 
                if e == 'admin/js/prepopulate.js':
                    jslist[i] = 'image/js/prepopulate.js'
        return base
