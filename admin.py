from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.forms import Media
from image.models import Image, Reform


                                    
class ImageAdmin(admin.ModelAdmin):
    fields = ('title', 'src', 'auto_delete')

    # case-insensitive contains match
    search_fields = ['title']
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

    #class Media:
    #    js = ('image/js/prepopulate.js',)

    @property
    def media(self):
        base = super().media
        for jslist in base._js_lists:
            for i, e in enumerate(jslist): 
                if e == 'admin/js/prepopulate.js':
                    #del(jslist[i]) 
                    jslist[i] = 'image/js/prepopulate.js'
        #return Media(js = ('image/js/prepopulate.js',)) + base
        return base
        
    #BaseModelAdmin
    #def get_prepopulated_fields(self, request, obj=None):
    # better, but how reference object?
    # formfield_overrides = {
        # models.TextField: {'widget': RichTextEditorWidget},
    # }
    # def get_form(self, request, obj=None, **kwargs):
        # form = super().get_form(request, obj, **kwargs)
        # if not obj:
            # #obj.title = obj.src.name
            # print('form:')
            # #print(str(form.base_fields['src'].initial.descriptor.file.name))
            # print(str(form.base_fields['src']))
            # form.base_fields['title'].initial = '2fgod2'

        #return form

         
admin.site.register(Image, ImageAdmin)
