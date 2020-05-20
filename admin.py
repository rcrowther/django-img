from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.forms import Media
from image.models import Image, Reform
from image import widgets

from django import forms
from django.db import models
                                    
class ImageAdmin(admin.ModelAdmin):
    #fields = ('title', 'auto_delete')
    # For pooled ffiles use, replace the above with this
    fields = ('title', 'src', 'auto_delete')

    # case-insensitive contains match
    search_fields = ['title']
    #! how about delete?
    list_display = ('title', 'upload_day', 'view_image')
    prepopulated_fields = {"title": ("src",)}

    # Can't say I like Django styling, but 'button' is what I can find 
    # as given.
    def view_image(self, obj):
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
        models.ImageField: {'widget': widgets.FileSingleChooserDAndD},
        
        #forms.ImageField: {'widget': admin.widgets.AdminFileWidget},
    }
    
    @property
    def media(self):
        base = super().media
        for jslist in base._js_lists:
            for i, e in enumerate(jslist): 
                if e == 'admin/js/prepopulate.js':
                    jslist[i] = 'image/js/prepopulate.js'
        return base
         
admin.site.register(Image, ImageAdmin)
