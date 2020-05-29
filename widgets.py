import json
import copy

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.forms.renderers import get_default_renderer
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.safestring import mark_safe


class RemoteFormWidget(forms.widgets.Widget):
    '''
    This widget presents a small/basic CRUD interface for a field.
    Since this suggests the field reprents a model, it is intended 
    for use on relation fields.
    The editing interface in this widget is links to appropriate 
    admin forms. But the view action will display a small table of 
    text renderable fields within the model.
    The widget is an interesting substitute for Django's default ModelCoosing
    widgets, more limited but clear in action and avoiding 
    potentially expensive db querying.
    
    model
        Class or instance
    mdata
        An iterable list of model-like data (the fields of which should
        themselves be iterables of field name/values)
    empty_vaLue
        A string to show if nothing else is rendered.
    url_format
        a callable of the form url_format(*args, action). USed to 
        provide the urls.
    '''
    #template_name = 'image/widgets/remote_control.html'
    #template_name = 'admin/includes/fieldset.html'
    template_name = 'image/widgets/temp_form.html'
    input_type = 'hidden'
    needs_multipart_form = True

    def __init__(self, 
        form=None,
        attrs=None
    ):
        self.form = form
        super().__init__(attrs)
        
    # def __deepcopy__(self, memo):
        # obj = copy.copy(self)
        # obj.attrs = self.attrs.copy()
        # obj.data = copy.copy(self.data)
        # memo[id(self)] = obj
        # return obj
        
    @property
    def is_hidden(self):
        return False
        
    def format_value(self, value):
        # Could be any kind of value representing a foreign field. 
        # Unchanged, so leave it.
        print('format')
        print(str(value))
        return super().format_value(value)

    def get_context(self, name, value, attrs):
        # widget -> modelctrls -> no_data_message/data -> pk -> mod4els/urls
        context = super().get_context(name, value, attrs)
        context['fieldset'] = self.form
        print(str(context))
        return context
                
    # def render(self, name, value, attrs=None, renderer=None):
        # r = super().render(name, value, attrs=None, renderer=None)
        # print('render')
        # return r

    # def _render(self, template_name, context, renderer=None):
        # if renderer is None:
             # renderer = get_default_renderer()
        # print('____render')
        # print(str(context))
        # return mark_safe(renderer.render(template_name, context))
        
    # class Media:
            # css={
                 # 'screen': ('image/css/widgets.css',)
            # }



class RemoteControlWidget(forms.widgets.Input):
    '''
    This widget presents a small/basic CRUD interface for a field.
    Since this suggests the field reprents a model, it is intended 
    for use on relation fields.
    The editing interface in this widget is links to appropriate 
    admin forms. But the view action will display a small table of 
    text renderable fields within the model.
    The widget is an interesting substitute for Django's default ModelCoosing
    widgets, more limited but clear in action and avoiding 
    potentially expensive db querying.
    
    This is a contrib.admin inclined widget---the urls are addressed 
    there.
    
    model
        Class, not instance
    mdata
        An iterable list of model data. The models should be iterables 
        of field name/values e.g. dicts.
    no_data_message
        A string to show if nothing  is rendered.
    '''
    # The idea here is to render the field as a hidden input, which
    # is unchanged on return. This means the form plays along with
    # all submission and save proceedure (rather than faffing with save
    # to make it a speciality). The display floats alongside.
    # I think rendering URLs belongs here, but conceed it is a faff, 
    # what with admin site and model both required.
    template_name = 'image/widgets/remote_control.html'
    input_type = 'hidden'

    def __init__(self, 
        admin_site_name,
        model,
        no_data_message='Unset',
        mdata=(),
        show_add=False,
        show_view=False,
        show_change=False,
        show_delete=False,
        attrs=None
    ):
        self.site_name = admin_site_name

        # Needed for URLs
        opts = model._meta
        self.app_label = opts.app_label
        self.model_name = opts.model_name
        
        # Data can be any iterable items, but we may need to render the
        # widget multiple times. So says Django. Thus, collapse it into 
        # a list.
        self.data = list(mdata)
        self.show_add = show_add
        self.show_view = show_view
        self.show_change  = show_change
        self.show_delete = show_delete
        self.no_data_message = no_data_message
        super().__init__(attrs)
        
    #? is this correct?
    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.attrs = self.attrs.copy()
        obj.data = copy.copy(self.data)
        memo[id(self)] = obj
        return obj
        
    @property
    def is_hidden(self):
        # Never hidden. It's a display. Overrrides detection of the 
        # 'hidden' attribute.
        return False

    def get_related_url(self, action, *args):
        return reverse(
                "admin:{}_{}_{}".format(self.app_label, self.model_name, action),
                args=args,
                current_app=self.site_name
                )
                          
    def get_context(self, name, value, attrs):
        # Generates:
        # widget -> modelctrls -> no_data_message/data -> pk -> models/urls
        context = super().get_context(name, value, attrs)
        modelctrls = {}
        modelctrls['no_data_message'] = self.no_data_message
        modelctrls_data = {} 
        if (self.data):
            for pk, md in self.data.items():
                models = {}
                if self.show_view:
                    models = md
                urls = {}
                if self.show_add:
                    urls['add'] = self.get_related_url('add')
                if self.show_delete:
                    urls['delete'] = self.get_related_url('delete', pk)
                if self.show_change:
                    urls['change'] = self.get_related_url('change', pk)
                modelctrls_data[pk] = {'models': models, 'urls': urls}
        modelctrls['data'] = modelctrls_data
        context['widget']['modelctrls'] = modelctrls
        #print('mk context')
        #print(str(context['widget']))        
        return context

    class Media:
            css={
                 'screen': ('image/css/widgets.css',)
            }



class FileChooserDAndD(forms.widgets.FileInput):
    # type name value and attrs printer
    template_name = 'image/widgets/file.html'

    @property
    def media(self):
        return forms.Media(
                js=('image/js/upload_dd.js',),
                css={'screen': ('image/css/widgets.css',),}
            )
