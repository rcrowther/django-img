from itertools import chain
from django.utils.translation import gettext, gettext_lazy as _
from django.forms.fields import Field
from django.forms.widgets import (
    HiddenInput, MultipleHiddenInput,
)
from django.forms.boundfield import BoundField
from django.core.exceptions import ValidationError

from image.widgets import RemoteControlWidget, RemoteFormWidget



#! should validate this is from a related field? or ok?
#! RemoteModelField
class ModelFixedField(Field):
    '''
    A base field that offers access and setting of related models.
    Compare to forms.models.ModelChoiceField, which offers choices. But 
    this has no need of an adjustable queryset, it takes the model field
    from which it can derive all necessary information.    
    
    model_field
        an instance, not the class
    initial
        can be an model obj
    '''
    #? Making an assumption of pk, but ok for OneToOne and ForeignField?
    default_error_messages = {
        'invalid_value': _('"%(value)s"  is not valid.'),
    }
    
    widget = HiddenInput

    def __init__(self, 
            model_field,
            *args,
            **kwargs
        ):
        super().__init__(**kwargs)
        self.model_field = model_field

    # Helpers. Given the, ummm, luxurious nature of Django model
    # information, needed.
    def get_related_model(self):
        #NB admin contains utils.get_model_from_relation(model_field)
        # which uses field.get_path_info()[-1].to_opts.model
        # and there is model_field.remote_field...
        # but this seems most direct?
        return self.model_field.target_field.model
        
    def get_related_model_fields(self):
        return self.get_related_model()._meta.fields        

    def get_related_model_editable_fieldnames(self):
        return [f.name for f in self.get_related_model_fields() if f.editable]
            
    def prepare_value(self, value):
        if hasattr(value, '_meta'):
            return value.pk
        return super().prepare_value(value)
        
    def to_python(self, value):
        """
        Return as int.
        Thus validates as int().
        return 
            int(), or None for empty values.
        """
        #NB like a form.IntegerField
        value = super().to_python(value)
        if value in self.empty_values:
            return None
        try:
            value = int(str(value))
        except (ValueError, TypeError):
            raise ValidationError(
                    self.error_messages['invalid_value'],
                    code='invalid_value',
                    params={'value': value},
                )
        return value

    def get_obj(self, value, hints={}):
        '''
        Get the remote object referred to by the field value.
        Note this does some can-not-find error catching. Also that the 
        return is None, so for many uses needs testing.
        return
            the object (queryset result), or None.
        '''
        # See admin.options.get_object() for similar shenannigans
        model = self.get_related_model()
        remote_manager = model._base_manager.db_manager(hints=hints)
        #query = {'pk__exact' : value}
        # if value is None:
            # return remote_manager.none() 
        # else:
            # return remote_manager.get(**query)
        # try:
            # object_id = field.to_python(object_id)
            # return queryset.get(**{field.name: object_id})
        # except (model.DoesNotExist, ValidationError, ValueError):
            # return None
        print('obj search value')
        try:
            object_id = self.to_python(value)
            print(str(object_id))
            query = {'pk__exact' : object_id}
            return remote_manager.get(**query)
        except (model.DoesNotExist, ValidationError, ValueError):
            return None
            
    def has_changed(self, initial, data):
        if self.disabled:
            return False
        initial_value = initial if initial is not None else ''
        data_value = data if data is not None else ''
        return str(self.prepare_value(initial_value)) != str(data_value)
    

#! RemoteFormField
class ModelFormField(ModelFixedField):
    '''
    Query for a remote id and instanciate a form.
    The form must be suitable for the recovered data. It is instanciated
    with the recovered object.
    The form is alsd hard-prefixed with 'embed-'.
    
    model_field
        A model field
    formk
        A form class, ready
    '''
    widget = RemoteFormWidget
    
    def __init__(self, 
            model_field,
            formk,
            **kwargs
        ):
        # Why? Why ask for a form when the model form builders can 
        # make one?
        # because a formfield is a raw thing, concerned with alidation.
        # exta data it configure it can know little about. In particular,
        # it doesn't ant to be supplied with requests, field definitions
        # and so forth. That probably belongs elsewhere.
        # And a minor second, Django's model form machinery involoves
        # clss then instanciation options. Class configuration is a bit 
        # involved for a form field.
        self.formk = formk
        # Makes no sense for a display.
        kwargs["required"] = False

        # NB widgets if given as class are zero-argument instanciated.
        super().__init__(model_field, **kwargs)
        
    def get_bound_field(self, form, field_name):
        bf = super().get_bound_field(form, field_name)

        # A key moment in this field.
        # The field has bound data, so we can ask it what it's value is.
        # As a foreign key, this will be a unique value, some data
        # that points to a model in another table.
        # From this, we can build a query, and so data to display.
        self.get_form(bf.value())
        return bf

    def get_form(self, value):
        obj = self.get_obj(value)
        print('get for obj')
        print(str(obj))
        params = {}
        
        # These three to maybe instanciate a form:
        # initial=None, prefix=None, instance=None
        if (obj):
            print('object to bind partial form')
            print(str(obj))
            params['instance'] = obj
        params['prefix'] = 'embed-' + self.model_field.name
        form = self.formk(**params)
        self.widget.form = form




        
#! How to glue by defULT to ImageSingleField?
#! not checking against original data --- has_changed? 
#! what about add forms, tho?
#! retrofit ModelFixedField
#! RemoteShowField
#class ModelShowField(ModelFixedField):
class ModelShowField(Field):
    """
    Handle an unchanging int representing a foreign key.
    The field includes code to extract the represented model, and turn
    it's data into a dict.
    """
    # The overall mechanism is like a ChoiceField, for display purposes.
    widget = RemoteControlWidget
    show_fields = None

    default_error_messages = {
        'invalid': _('The pk value did not match the embed instance.'),
        'type': _('Would not become int.'),
    }

    def __init__(self, 
            model_field,
            *args, 
            show_add=None,
            show_change=False, 
            show_delete=False,
            show_view=False,
            show_fields=None,
            **kwargs
        ):
        self.model_field = model_field
        self.show_add = show_add
        self.show_view = show_view
        self.show_change  = show_change
        self.show_delete = show_delete

        # Makes no sense for a display.
        kwargs["required"] = False

        self.show_fields = show_fields or self.show_fields
        if (not(show_fields)):
            self.show_fields = [f.name for f in model_field.remote_field.model._meta.fields]
        
        # NB widgets if given as class are zero-argument instanciated.
        super().__init__(**kwargs)
    
    def to_python(self, value):
        """
        Validate that int() can be called on the input. Return the result
        of int() or None for empty values.
        """
        value = super().to_python(value)
        if value in self.empty_values:
            return None
        try:
            value = int(str(value))
        except (ValueError, TypeError):
            raise ValidationError(self.default_error_messages['type'], code='type')
        return value

    def get_foreign_qs(self, value, **hints):
        """
        Get the model this foreign key targets.
        
        hints
            db lookup paramets, such as an explicit db.
        """
        # hard to believe Django has nothing like a simple foreign key
        # lookup, but I can't find it. Hence this insanity.
        #? get_objs_from_relations()
        #! forms.utils.get_related_model
        #? field.get_path_info()[-1].to_opts.model
        remote_manager = self.model_field.target_field.model._base_manager.db_manager(hints=hints)
        params = {
            '{}__exact'.format(remote_field.name): value
            for _, remote_field in self.model_field.related_fields
        }

        #? Want the pk but I think qs always gets it?
        # .get() would fail on multiple matches
        return remote_manager.get(**params)
        
    def get_bound_field(self, form, field_name):
        bf = super().get_bound_field(form, field_name)

        # A key moment in this field.
        # The field has bound data, so we can ask it what it's value is.
        # As a foreign key, this will be a unique value, some data
        # that points to a model in another table.
        # From this, we can build a query, and so data to display.
        self.get_data(bf.value())
        return bf

    def qs_to_dict(self, instance, fields=None, exclude=None):
        '''
        Generate a dictionary of displayable data from an model object.
        '''
        # Vary like models.forms.model_to_dict, but it isn't.
        opts = instance._meta
        data = {}
        for f in chain(opts.concrete_fields, opts.many_to_many):
            if fields is not None and f.name not in fields:
                continue
            if exclude and f.name in exclude:
                continue
            data[f.name] = f.value_from_object(instance)
        return data

    def get_data(self, value):
        obj_dict = {}

        # if the field points at anything, generate data
        if (value):
            obj = self.get_foreign_qs(value)
            obj_dict = self.qs_to_dict(obj, fields=self.show_fields)
            
            # Now a trick. We only want to print one model, but 
            # the widget is set to iterate, so make single object into
            # a list.
            # This has it's advantages. Because the model data is keyed 
            # by the foreign key, unique and probably the pk, the key
            # can be used for URL generation. There is no need to 
            # carry non-display entries for the sake of URL generation. 
            # Clean separation, 
            obj_dict = {value : obj_dict}
                
        # like ModelChoiceField, attach choices to the widget by
        # pushing them in.
        self.widget.data = obj_dict
        self.widget.show_add=self.show_add
        self.widget.show_change=self.show_change
        self.widget.show_delete=self.show_delete
        self.widget.show_view=self.show_view
