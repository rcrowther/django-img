from django.forms.fields import Field
from django.forms.widgets import (
    HiddenInput, MultipleHiddenInput, RadioSelect, SelectMultiple,
)
from django.utils.translation import gettext, gettext_lazy as _
from image.widgets import RemoteControlWidget
from django.forms.boundfield import BoundField
from django.forms.models import model_to_dict
from itertools import chain



# class ForeignKeyFixedField2(Field):
    # """
    # Foreign key with recovery of remote models.
    # Not intended for .
    
    # remote_instance
    # """
    # #widget = RemoteControlWidget
    # show_fields = None

    # default_error_messages = {
        # 'invalid': _('The pk value did not match the embed instance.'),
    # }

    # def __init__(self, 
            # model_field,
            # *args, 
            # can_add=None,
            # show_change=False, 
            # show_delete=False,
            # show_view=False,
            # show_fields=None,
            # **kwargs
        # ):
        # self.model_field = model_field
        # self.remote_model_manager = self.model_field.remote_field.model._default_manager #.using(db)
        # self.can_add = can_add
        # self.show_view = show_view
        # self.show_change  = show_change
        # self.show_delete = show_delete

        # # Makes no sense for a display.
        # kwargs["required"] = False

        # #self.empty_value = empty_value or self.empty_value
        # self.show_fields = show_fields or self.show_fields
        # if (not(show_fields)):
            # self.show_fields = [f.name for f in model_field.remote_field.model._meta.fields]

        # # ensure the pk is retrieved
        # pk_name = self.model_field.model._meta.pk.name
        # if (pk_name not in self.show_fields):
            # self.show_fields.append(pk_name)
        # self.pk_name = pk_name
        
        # #! but remove trick stuff like imagefields?
        
        # print('form field kwargs')
        # print(str(kwargs))
        # #print('form field queryset')
        # #print(str(queryset))
        # #print('form field widget')
        # #print(str(widget))

        # # NB widgets if given as class are zero-argument instanciated.
        # super().__init__(**kwargs)
        # print('form field initial')
        # print(str(self.initial))

    # def get_foreign_model(self, value, **hints):
        # """
        # Get the model this foreign key targets.
        
        # hints
            # db lookup paramets, such as an explicit db.
        # """
        # # har to believe Django has nothing like a simple foreign key
        # # lookup, but I can't find it.
        # # {'img__id': 1}
        # # django.db.models.fields.related_descriptions.get_queryset()
        # # self.related.related_model._base_manager.db_manager(hints=hints).all()
        # #self.model_field.remote_field.model._default_manager #.using(db)

        # remote_manager = self.model_field.target_field.model._base_manager.db_manager(hints=hints)
        # params = {
            # '{}__exact'.format(remote_field.name): value
            # for _, remote_field in self.model_field.related_fields
        # }
        # return remote_manager.filter(**params)
        
    # def validate(self, value):
        # print('validate form field')
        # super().validate(value)
        
    # def clean(self, value):
        # print('clean form field value')
        # print(value)
        # #? The returned value was/is the original instance
        # # but we do nothing with it...
        # if value in self.empty_values:
            # # cover 'add' data
            # return None

        # # compare the values as equal types.
        # #orig = self.remote_instance.pk
        # ##if str(value) != str(orig):
        # if(self.has_changed(self.initial.pk, value)):
             # raise ValidationError(
                 # self.error_messages['unrecognised_pk_value'],
                 # code='unrecognised_pk_value',
                 # params={'pk': value},
             # )
        # return value

    # def prepare_value(self, value):
        # print('form field prepare_value')
        # print(str(value))
        # return value
        
    # def to_python(self, value):
        # print('to pythin')
        # print(str(value))
        # return super().to_python(value)

    # def bound_data(self, data, initial):
        # """
        # Return the value that should be shown for this field on render of a
        # bound form, given the submitted POST data for the field and the initial
        # data, if any.

        # For most fields, this will simply be data; FileFields need to handle it
        # a bit differently.
        # """
        # print('bound_data initial')
        # print(str(initial))
        # print('data')
        # print(str(data))
        # if self.disabled:
            # return initial
        # return data
        
    # def has_changed(self, initial, value):
        # print('has changed')
        # #return str(initial)== str(value)
        # return super().has_changed(initial, value)

    # def get_bound_field(self, form, field_name):
        # # called
        # bf = BoundField(form, self, field_name)
        # print('form field get_bound_field')        
        # print(str(bf.value()))
        # print(str(bf.data))
        # # A key moment in this field.
        # # The form has bound data, so we can ask it what it's value is.
        # # As a foreign key, this will be a the key value, some data
        # # that points to moodel in another table.
        # # From this, we can build a query, and so data to display.
        # self.get_data(bf.value())
        # return bf

    # def get_data(self, value):
        # obj_dict = {}

        # #value = 1

        # # if the field points at anything, generate data
        # if (value):
            # #for obj in self.remote_model_manager.filter(pk=value):
                # obj = self.get_foreign_model(value)
                # obj_dict = model_to_dict(obj, fields=self.show_fields)
                # print('form field obj_dict')        
                # print(str(obj_dict))
                # #b[getattr(obj, self.pk_name)] = obj_dict
                
        # # like ModelChoiceField, attach choices to the widget
        # self.widget.data = obj_dict
        # self.widget.can_add=self.can_add
        # self.widget.show_change=self.show_change
        # self.widget.show_delete=self.show_delete
        # self.widget.show_view=self.show_view


#Should do it
#! How to glue by defULT to ImageSingleField?
#! not checking against original data --- has_changed? 
#! what about add forms, tho?
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
