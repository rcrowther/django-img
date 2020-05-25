import json
import copy

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.forms.renderers import get_default_renderer



#! not handling blank value
class TextDisplayWidget(forms.Widget):
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
    template_name = 'image/widgets/text_display.html'
    empty_value='',
    
    def __init__(self, 
        admin_site_name,
        model,
        mdata=(),
        can_add=False,
        can_view=False,
        can_change=False,
        can_delete=False,
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
        self.can_add = can_add
        self.can_view = can_view
        self.can_change  = can_change
        self.can_delete = can_delete

        print('init sprite')
        print(str(self.model_name))
        print(str(self.app_label))
        super().__init__(attrs)
        
    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.attrs = self.attrs.copy()
        obj.data = copy.copy(self.data)
        memo[id(self)] = obj
        return obj
        
    def format_value(self, value):
        # Could be any kind of value representing a foreign field. 
        # Unchanged, so leave it.
        print('format')
        print(str(value))
        return super().format_value(value)
        # if value == '' or value is None:
            # return 'No data'
        # if self.is_localized:
            # return formats.localize_input(value)
        # return str(value)

    def get_related_url(self, action, *args):
        return reverse(
                "admin:{}_{}_{}".format(self.app_label, self.model_name, action),
                args=args,
                current_app=self.site_name
                )
                          
    def get_context(self, name, value, attrs):
        print('mk context')
        print(str(self.data))
        context = super().get_context(name, value, attrs)
        modelctrls = {}
        for pk, model_data in self.data.items():
            if self.can_view:
                data = model_data
            urls = {}
            if self.can_add:
                urls['add'] = self.get_related_url('add')
            if self.can_delete:
                urls['delete'] = self.get_related_url('delete', pk)
            if self.can_change:
                urls['change'] = self.get_related_url('change', pk)
            modelctrls[pk] = {'data': data, 'urls': urls}
        context['widget']['modelctrls'] = modelctrls
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
        
    class Media:
            css={
                 'screen': ('image/css/widgets.css',)
            }


from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.utils.text import Truncator

def url_params_from_lookup_dict(lookups):
    """
    Convert the type of lookups specified in a ForeignKey limit_choices_to
    attribute to a dictionary of query parameters
    """
    params = {}
    if lookups and hasattr(lookups, 'items'):
        for k, v in lookups.items():
            if callable(v):
                v = v()
            if isinstance(v, (tuple, list)):
                v = ','.join(str(x) for x in v)
            elif isinstance(v, bool):
                v = ('0', '1')[v]
            else:
                v = str(v)
            params[k] = v
    return params
    
#class ForeignKey():
#    Widget
# /django-admin/image/image/?_to_field=id
class ImageSingleFieldWidget(forms.TextInput):
    """
    A Widget for displaying ForeignKeys in the "raw_id" interface rather than
    in a <select> box.
    """
    #template_name = 'admin/widgets/foreign_key_raw_id.html'
    template_name = 'image/widgets/image_single_field.html'

    def __init__(self, rel, admin_site, attrs=None, using=None):
        self.rel = rel
        self.admin_site = admin_site
        self.db = using
        super().__init__(attrs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        rel_to = self.rel.model
        if rel_to in self.admin_site._registry:
            # The related object is registered with the same AdminSite
            related_url = reverse(
                'admin:%s_%s_changelist' % (
                    rel_to._meta.app_label,
                    rel_to._meta.model_name,
                ),
                current_app=self.admin_site.name,
            )

            params = self.url_parameters()
            if params:
                related_url += '?' + '&amp;'.join('%s=%s' % (k, v) for k, v in params.items())
            context['related_url'] = mark_safe(related_url)
            context['link_title'] = _('Lookup')
            # The JavaScript code looks for this class.
            context['widget']['attrs'].setdefault('class', 'vForeignKeyRawIdAdminField')
        else:
            context['related_url'] = None
        if context['widget']['value']:
            context['link_label'], context['link_url'] = self.label_and_url_for_value(value)
        else:
            context['link_label'] = None
        return context

    def base_url_parameters(self):
        limit_choices_to = self.rel.limit_choices_to
        if callable(limit_choices_to):
            limit_choices_to = limit_choices_to()
        return url_params_from_lookup_dict(limit_choices_to)

    def url_parameters(self):
        from django.contrib.admin.views.main import TO_FIELD_VAR
        params = self.base_url_parameters()
        params.update({TO_FIELD_VAR: self.rel.get_related_field().name})
        return params

    def label_and_url_for_value(self, value):
        key = self.rel.get_related_field().name
        try:
            obj = self.rel.model._default_manager.using(self.db).get(**{key: value})
        except (ValueError, self.rel.model.DoesNotExist, ValidationError):
            return '', ''

        try:
            url = reverse(
                '%s:%s_%s_change' % (
                    self.admin_site.name,
                    obj._meta.app_label,
                    obj._meta.object_name.lower(),
                ),
                args=(obj.pk,)
            )
        except NoReverseMatch:
            url = ''  # Admin not registered for target model.

        return Truncator(obj).words(14), url
