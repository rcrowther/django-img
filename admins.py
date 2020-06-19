import copy
from django.contrib import admin
#from django.utils.translation import gettext_lazy as _
from django.forms import Media
from django.utils.html import format_html
from django import forms
from django.db.models import ImageField
                         
from image.widgets import FileChooserDAndD


                                    
class ImageLockedAdmin(admin.ModelAdmin):
    '''
    Locks files to images by disallowing editing.. 
    Also makes the the changelist more utilitarian.
    Build for use administering an image collection. Not for front
    end presentation. 
    '''
    #! All the below can be commented or adapted to remove/change 
    # particular effects.
    # See the notes.
    #
    # case-insensitive contains match
    search_fields = ['src']
    
    # Style the lists.
    # See the support code below
    #! how about delete button?
    list_display = ('filename', 'upload_day', 'image_delete', 'image_view',)

    # Enhance file pickers, sometimes, with a drop area. 
    # See note on Media.
    #! throws a dependency error on change files
    #prepopulated_fields = {"title": ("src",)}

    def __init__(self, model, admin_site):
        # Consistent API here, please. I'd use a set, but Python tells
        # me that's unhashable. Also, think it needs to be a copy.
        # Needed for the upload locking.
        self.readonly_fields = list(copy.deepcopy(self.readonly_fields))
        super().__init__(model, admin_site)
        
    # Support code for styling the admin list
    # See the 'list_display' attribute.
    def image_view(self, obj):
        return format_html('<a href="{}" class="button">View</a>',
            obj.src.url
        )
    image_view.short_description = 'View'

    def image_delete(self, obj):
        return format_html('<a href="{}/delete" class="button" style="background: #ba2121;color: #fff;">Delete</a>',
            obj.pk
        )
    image_delete.short_description = 'Delete'
    
    def upload_day(self, obj):
        '''e.g.	17 May 2020'''
        return format_html('{}',
            obj._upload_time.strftime("%d %b %Y")
        )
    upload_day.short_description = 'Upload day'
    upload_day.admin_order_field = '_upload_time'

    def filename(self, obj):
        return obj.filename
    filename.admin_order_field = 'src'
    
    # Block filechoosing on uploaded Image models.
    def get_form(self, request, obj=None, change=False, **kwargs):
        # I don't currently see a way in aside from
        # push/popping the attribute, like Javascript.
        #
        # Only way I can think of differentiating between the two forms.
        # change attribute behaves inconsistently. But object
        # detection detects add/change forms.
        #
        # by the by, this stinks. I say so.
        if (obj):
            if (not('src'in self.readonly_fields)): 
                self.readonly_fields.append('src')
        else:
           if ('src'in self.readonly_fields): 
                self.readonly_fields.remove('src')
        return super().get_form( request, obj, change, **kwargs)
        
        
        
        
        
    # Choose a style of upload pickers
    formfield_overrides = {
        # Basic django browse button.
        #ImageField: {'widget': forms.FileInput},
        
        # Admin picker enhanced with current file display. Admin 
        # default. Some don't like it, some do.
        #ImageField: {'widget': admin.widgets.AdminFileWidget},
        
        # Image picker has a simple drop field
        #ImageField: {'widget': FileChooserDAndD},
    }
    
    # Code for prepopulation, with special handling of 
    # SingleImageFields. See 'prepopulate' attribute.
    # @property
    # def media(self):
        # base = super().media
        # for jslist in base._js_lists:
            # for i, e in enumerate(jslist): 
                # if e == 'admin/js/prepopulate.js':
                    # jslist[i] = 'image/js/prepopulate.js'
        # return base
