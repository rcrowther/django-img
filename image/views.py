from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.views.generic.base import TemplateView
from django.utils.html import format_html
from django.contrib import messages
from django.utils.translation import gettext as _, ngettext
from django.urls import reverse
from django.urls import path
from .forms import ReformsForm
from image.registry import registry, NotRegistered



class ImageReformsView(TemplateView):
    model = None
    
    @classmethod
    def url(cls):
        url_name = cls.model.url_view_form_reform_add_name()
        url = cls.model.url_view_form_reform_add()
        return path(url, cls.as_view(), name=url_name)

    def get_object(self):
        pk = self.kwargs.get('pk')
        try:
            obj = self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            raise Http404(_("No %(verbose_name) found matching the query") %
                          {'verbose_name': self.model._meta.verbose_name})
        return obj

    def get_filter_choices(self, obj):
        all_filter_keys = registry.keys
        filters_applied = obj.get_filters_applied()
        filter_keys = set(all_filter_keys) - set(filters_applied)
        return [(fk, fk) for fk in filter_keys]  

    def redirect_to_changelist(self):
        opts = self.model._meta
        
        # Don't reverse, don't know what name is, head for the 
        # changelist
        redirect_url = '/admin/%s/%s/' % (opts.app_label, opts.model_name)
        return HttpResponseRedirect(redirect_url)
                    
    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        filter_choices = self.get_filter_choices(obj)
        if (not filter_choices):
            reform_dict = {'filename': obj.filename, 'filters': str(registry.keys)} 
            msg = format_html(
                _('Image "{filename}" has generated all possible reforms through these filters {filters}.'),
                **reform_dict
            )
            messages.add_message(request, messages.INFO, msg)            
            return self.redirect_to_changelist()
        form = ReformsForm(filter_choices)
        return render(request, 'image/reforms_addform.html', {'image': obj, 'form': form})
            
    def post(self, request, *args, **kwargs):
        obj = self.get_object()

        # create a form instance and populate it with data
        form = ReformsForm(self.get_filter_choices(obj), request.POST)
        if form.is_valid():
            selected_filters = form.cleaned_data['available_filters']
            
            # throws NotRegistered, in production returns 50x???
            ifilters = [registry(f) for f in selected_filters]

            # throws SourceImageIOError, in production returns 50x???
            succeded_names = [] 
            failed_filters= []
            for f in ifilters:
                try:
                    rfm = obj.get_reform(f)
                    succeded_names.append(rfm.src.name)
                except SourceImageIOError:
                    failed_filters.append(f)
            if (len(succeded_names) == len(ifilters)):
                # write success mesage
                msg_dict = {'filename': obj.filename, 'paths': str(succeded_names)} 
                msg = format_html(
                    _('Image "{filename}" generated reform(s) successfully. {paths}'),
                    **msg_dict
                )
                messages.add_message(request, messages.SUCCESS, msg)
            else:
                # failed to generate a reform, for some reason
                msg_dict = {'filename': obj.filename, 'paths': str(succeded_names), 'failed_filters':failed_filters} 
                msg = format_html(
                    _('Image "{filename}" generated reform(s) at {paths}, but filters "{failed_filters}" failed.'),
                    **msg_dict
                )
                messages.add_message(request, messages.WARNING, msg)
            
            #? Also, create these and add more button
            return self.redirect_to_changelist()
        else:
            #if not valid, reerender form with error messages
            return render(request, 'image/reforms_addform.html', {'form': form})

