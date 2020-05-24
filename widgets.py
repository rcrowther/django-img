import json

from django import forms
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.forms.renderers import get_default_renderer



# From Input
class TextDisplayWidget(forms.Widget):
    '''
    model 
        usually a class, not an instance
    '''
    template_name = 'image/widgets/text_display.html'
    
    def __init__(self, 
        admin_site,
        model,
        attrs=None, 
        data=(),
        can_add=None,
        can_change=False,
        can_delete=False,
        can_view=False
    ):
        super().__init__(attrs)
        # Data can be any iterable pairs, but we may need to render the
        # widget multiple times. So says Django. Thus, collapse it into 
        # a list.
        self.data = list(data)
        self.admin_site = admin_site
        self.model = model
        self.can_add = can_add
        self.can_view = can_view
        self.can_change  = can_change
        self.can_delete = can_delete
        
    def format_value(self, value):
        print('format')
        #return super().format_value(value)
        if value == '' or value is None:
            return 'No data'
        if self.is_localized:
            return formats.localize_input(value)
        return str(value)

    def get_related_url(self, info, action, *args):
        return reverse("admin:%s_%s_%s" % (info + (action,)),
                       current_app=self.admin_site.name, args=args)
        
    def get_context(self, name, value, attrs):
        opts = self.model._meta
        info = (opts.app_label, opts.model_name)
        context = super().get_context(name, value, attrs)
        if self.can_view:
            context['widget']['data'] = self.data
        urls = {}
        if self.can_add:
            urls['add'] = self.get_related_url(info, 'add')
        #if (value):
        if self.can_delete:
            urls['delete'] = self.get_related_url(info, 'delete', value)
        if self.can_change:
            urls['change'] = self.get_related_url(info, 'change', value)
        context['widget']['urls'] = urls
        print('mk context')
        print(str(self.can_view))
        return context
                
    # def render(self, name, value, attrs=None, renderer=None):
        # r = super().render(name, value, attrs=None, renderer=None)
        # print('render')
        # return r

    def _render(self, template_name, context, renderer=None):
        if renderer is None:
             renderer = get_default_renderer()
        print('____render')
        print(str(context))
        return mark_safe(renderer.render(template_name, context))
# class HiddenDisplayWidget(MultiWidget):
    # template_name = 'image/forms/widgets/hiddendisplaywidget.html'
        # widgets = (
            # TextDisplayWidget(
                # attrs=attrs,
            # ),
            # HiddenInput(
                # attrs=attrs,
            # ),
        # )
        
# class HiddenHiddenDisplayWidget(HiddenDisplayWidget):
    # template_name = 'image/forms/widgets/hiddenhiddendisplaywidget.html'

    # def __init__(self, model):
        # super().__init__(attrs)
        # for widget in self.widgets:
            # widget.input_type = 'hidden'

        
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
