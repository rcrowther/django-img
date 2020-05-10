from weakref import WeakSet
from django.apps import apps
from image.format import ImgFormat
from django.core.exceptions import ImproperlyConfigured

from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

class AlreadyRegistered(Exception):
    pass


class NotRegistered(Exception):
    pass


all_sites = WeakSet()


class ImgSite:
    """
    An AdminSite object encapsulates an instance of the Django admin application, ready
    to be hooked in to your URLconf. Models are registered with the AdminSite using the
    register() method, and the get_urls() method can then be used to access Django view
    functions that present a full admin interface for the collection of registered
    models.
    """
    
    def __init__(self, name='img'):
        self._registry = {}  # model_class class -> admin_class instance
        self.name = name
        #self._actions = {'delete_selected': actions.delete_selected}
        #self._global_actions = self._actions.copy()
        all_sites.add(self)

    # def check(self, app_configs):
        # """
        # Run the system checks on all ModelAdmins, except if they aren't
        # customized at all.
        # """
        # if app_configs is None:
            # app_configs = apps.get_app_configs()
        # app_configs = set(app_configs)  # Speed up lookups below

        # errors = []
        # modeladmins = (o for o in self._registry.values() if o.__class__ is not ModelAdmin)
        # for modeladmin in modeladmins:
            # if modeladmin.model._meta.app_config in app_configs:
                # errors.extend(modeladmin.check())
        # return errors

    def register(self, model_or_iterable, admin_class=None, **options):
        """
        Register the given model(s) with the given admin class.

        The model(s) should be Model classes, not instances.

        If an admin class isn't given, use ModelAdmin (the default admin
        options). If keyword arguments are given -- e.g., list_display --
        apply them as options to the admin class.

        If a model is already registered, raise AlreadyRegistered.

        If a model is abstract, raise ImproperlyConfigured.
        """
        admin_class = admin_class or ImgFormat
        if isinstance(model_or_iterable, ImgFormat):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model._meta.abstract:
                raise ImproperlyConfigured(
                    'The model %s is abstract, so it cannot be registered with admin.' % model.__name__
                )

            if model in self._registry:
                registered_admin = str(self._registry[model])
                msg = 'The model %s is already registered ' % model.__name__
                # if registered_admin.endswith('.ModelAdmin'):
                    # # Most likely registered without a ModelAdmin subclass.
                    # msg += 'in app %r.' % re.sub(r'\.ModelAdmin$', '', registered_admin)
                # else:
                    # msg += 'with %r.' % registered_admin
                raise AlreadyRegistered(msg)

            # Ignore the registration if the model has been
            # swapped out.
            #! what?
            if not model._meta.swapped:
                # If we got **options then dynamically construct a subclass of
                # admin_class with those **options.
                if options:
                    # For reasons I don't quite understand, without a __module__
                    # the created class appears to "live" in the wrong place,
                    # which causes issues later on.
                    options['__module__'] = __name__
                    admin_class = type("%sAdmin" % model.__name__, (admin_class,), options)

                # Instantiate the admin class to save in the registry
                self._registry[model] = admin_class(model, self)


    def unregister(self, model_or_iterable):
        """
        Unregister the given model(s).

        If a model isn't already registered, raise NotRegistered.
        """
        if isinstance(model_or_iterable, ImgFormat):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model not in self._registry:
                raise NotRegistered('The model %s is not registered' % model.__name__)
            del self._registry[model]

    def is_registered(self, model):
        """
        Check if a model class is registered with this `AdminSite`.
        """
        return model in self._registry

    # def each_context(self, request):
        # """
        # Return a dictionary of variables to put in the template context for
        # *every* page in the admin site.

        # For sites running on a subpath, use the SCRIPT_NAME value if site_url
        # hasn't been customized.
        # """
        # script_name = request.META['SCRIPT_NAME']
        # site_url = script_name if self.site_url == '/' and script_name else self.site_url
        # return {
            # 'site_title': self.site_title,
            # 'site_header': self.site_header,
            # #'site_url': site_url,
            # #'has_permission': self.has_permission(request),
            # 'available_apps': self.get_app_list(request),
            # 'is_popup': False,
        # }
        
    def _build_app_dict(self, request, label=None):
        """
        Build the app dictionary. The optional `label` parameter filters models
        of a specific app.
        """
        app_dict = {}

        if label:
            models = {
                m: m_a for m, m_a in self._registry.items()
                if m._meta.app_label == label
            }
        else:
            models = self._registry

        for model, model_admin in models.items():
            app_label = model._meta.app_label

            #has_module_perms = model_admin.has_module_permission(request)
            #if not has_module_perms:
            #    continue

            #perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            #if True not in perms.values():
            #    continue

            info = (app_label, model._meta.model_name)
            model_dict = {
                'name': capfirst(model._meta.verbose_name_plural),
                'object_name': model._meta.object_name,
                #'perms': perms,
                #'admin_url': None,
                #'add_url': None,
            }
            # if perms.get('change') or perms.get('view'):
                # model_dict['view_only'] = not perms.get('change')
                # try:
                    # model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                # except NoReverseMatch:
                    # pass
            # if perms.get('add'):
                # try:
                    # model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                # except NoReverseMatch:
                    # pass

            if app_label in app_dict:
                app_dict[app_label]['models'].append(model_dict)
            else:
                app_dict[app_label] = {
                    'name': apps.get_app_config(app_label).verbose_name,
                    'app_label': app_label,
                    # 'app_url': reverse(
                        # 'admin:app_list',
                        # kwargs={'app_label': app_label},
                        # current_app=self.name,
                    # ),
                    #'has_module_perms': has_module_perms,
                    'models': [model_dict],
                }

        if label:
            return app_dict.get(label)
        return app_dict


    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        return app_list
        

class DefaultImgSite(LazyObject):
    def _setup(self):
        ImgSiteClass = import_string(apps.get_app_config('img').default_site)
        self._wrapped = ImgSiteClass()


# This global object represents the default admin site, for the common case.
# You can provide your own AdminSite using the (Simple)AdminConfig.default_site
# attribute. You can also instantiate AdminSite in your own code to create a
# custom admin site.
site = DefaultImgSite()
