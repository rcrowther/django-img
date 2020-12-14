import copy
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import ImageField
from image.model_fields import ImageFileField
from django.utils.html import format_html



class ImageCoreAdmin(admin.ModelAdmin):
    '''
    Admin devised for maintenence of Image/Reform models.
    Not intended for end users (unless those users are trusted). It
    administers the models, not the use of the images in other models. 
    It has these features:
    - Locks files to image models by disallowing editing.. 
    - Reorganises the changelist to be cleaner and more utilitarian.
    '''
    #! All the below can be commented or adapted to remove/change 
    # particular effects.
    # See the notes.
    #
    # case-insensitive 'contains' match
    search_fields = ['src']
    
    # Style the lists.
    # See the support code below
    list_display = ('filename', 'upload_day', 'image_delete', 'image_view',)

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
            obj.upload_time.strftime("%d %b %Y")
        )
    upload_day.short_description = 'Upload day'
    upload_day.admin_order_field = '_upload_time'

    def filename(self, obj):
        return obj.filename
    filename.admin_order_field = 'src'
    
    def get_form(self, request, obj=None, change=False, **kwargs):
        # Block filechoosing on uploaded Image models.
        #
        # I don't currently see a way in aside from
        # push/popping the attribute, like Javascript.
        #
        # Only way I can think of differentiating between the two forms.
        # change attribute behaves inconsistently. But object
        # detection detects add/change forms.
        #
        # by the by, this stinks. I say so.
        if (obj):
            if (not('src' in self.readonly_fields)): 
                self.readonly_fields.append('src')
        else:
           if ('src' in self.readonly_fields): 
                self.readonly_fields.remove('src')
        return super().get_form( request, obj, change, **kwargs)

    # if you want to change the filechooser on the add form, you
    # can do it here. The default is
    # admin.widgets.AdminFileWidget
    #formfield_overrides = {
        ## For example, Drag and drop Image picker from,
        ## https://github.com/rcrowther/DDFileChooser
        #ImageFileField: {'widget': DDFileChooser},
    #}        
        
        
        
class LinkedImageAdmin(admin.ModelAdmin):
    '''
    Admin for models that contain image foreign keys.
    The main action is to disallow editing of image fields if an image 
    has been allocated.
    A small override that can be mixed with other Admin 
    code with no unexpected effects.
    '''
    def __init__(self, model, admin_site):
        # Consistent API here, please. I'd use a set, but Python tells
        # me that's unhashable. Also, think it needs to be a copy.
        # Needed for the upload locking.
        self.readonly_fields = list(copy.deepcopy(self.readonly_fields))
        
        # ok, lets get the fields concerned
        self.image_fields = []
        for f in model._meta.fields:
            if issubclass(f, ImageRelationFieldMixin):
                self.image_fields.appenf(f.name)
        super().__init__(model, admin_site)

    def get_form(self, request, obj=None, change=False, **kwargs):
        # Block filechoosing on linked Image fields.
        #
        # I don't currently see a way in aside from
        # push/popping the attribute, like Javascript.
        #
        # Only way I can think of differentiating between the two forms.
        # change attribute behaves inconsistently. But object
        # detection detects add/change forms.
        #
        # by the by, this stinks. I say so. RC.
        for fn in self.image_fields:
            if (not(obj) or (not (getattr(fn, obj).path))):
                if (not(fn in self.readonly_fields)): 
                    self.readonly_fields.append(fn)
            else:
                if (fn in self.readonly_fields): 
                    self.readonly_fields.remove(fn)
                
        return super().get_form( request, obj, change, **kwargs)

    # if you want to change the filechooser on the forms, you
    # can do it here. The default is admin.widgets.AdminFileWidget.
    #formfield_overrides = {
        ## For example, Drag and drop Image picker from,
        ## https://github.com/rcrowther/DDFileChooser
        #ImageFileField: {'widget': DDFileChooser},
    #}  

