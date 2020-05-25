from django.forms.fields import Field
from django.forms.widgets import (
    HiddenInput, MultipleHiddenInput, RadioSelect, SelectMultiple,
)
from django.utils.translation import gettext, gettext_lazy as _
from image.widgets import TextDisplayWidget
from django.forms.boundfield import BoundField

#Should do it
#! How to glue by defULT to ImageSingleField?
#! not checking against original data --- has_changed? 
#! what about add forms, tho?
class ForeignKeyFixedField(Field):
    """
    Check a remote key is unchanged via a form.
    Used for embeds/inlines.
    
    remote_instance
    """
    #widget = TextDisplayWidget()
    #hidden_widget = HiddenInput
    #widget = HiddenInput
    #hidden = True
    #show_hidden_initial = False
    needs_multipart_form=False
    show_fields = None
    empty_value = "nowt"
    #attrs = {}

    default_error_messages = {
        'invalid': _('The pk value did not match the embed instance.'),
    }

    def __init__(self, 
            model,
            queryset,
            *args, 
            can_add=None,
            can_change=False, 
            can_delete=False,
            can_view=False,
            remote_instance=None, 
            empty_value= '',
            show_fields=None,
            **kwargs
        ):
        # whole model 
        self.initial = remote_instance
        self.queryset = queryset
        self.model = model
        self.can_add = can_add
        self.can_view = can_view
        self.can_change  = can_change
        self.can_delete = can_delete
        # # cover 'add' data
        # if self.remote_instance is not None:
            # kwargs["initial"] = self.remote_instance.pk

        # Makes no sense for a display.
        kwargs["required"] = False

        self.empty_value = empty_value or self.empty_value
        self.show_fields = show_fields or self.show_fields
        if (not(show_fields)):
            self.show_fields = [f.name for f in model._meta.fields]

        # ensure the pk is retrieved
        pk = model._meta.pk.name
        if (pk not in self.show_fields):
            self.show_fields.append(pk)
        self.pk = pk
        
        #! but remove trick stuff like imagefields?
        
        print('form field kwargs')
        print(str(kwargs))
        #print('form field queryset')
        #print(str(queryset))
        #print('form field widget')
        #print(str(widget))
        print('form field perm')
        print(str(self.can_view))
        # NB widgets if given as class are zero-argument instanciated.
        super().__init__(**kwargs)
        self.get_data()

    def validate(self, value):
        print('validate form field')
        super().validate(value)
        
    def clean(self, value):
        print('clean form field value')
        print(value)
        #? The returned value was/is the original instance
        # but we do nothing with it...
        if value in self.empty_values:
            # cover 'add' data
            return None

        # compare the values as equal types.
        #orig = self.remote_instance.pk
        ##if str(value) != str(orig):
        if(self.has_changed(self.initial.pk, value)):
             raise ValidationError(
                 self.error_messages['unrecognised_pk_value'],
                 code='unrecognised_pk_value',
                 params={'pk': value},
             )
        return value

    def to_python(self, value):
        print('to pythin')
        print(str(value))
        return super().to_python(value)

    def bound_data(self, data, initial):
        """
        Return the value that should be shown for this field on render of a
        bound form, given the submitted POST data for the field and the initial
        data, if any.

        For most fields, this will simply be data; FileFields need to handle it
        a bit differently.
        """
        print('bound data initial')
        print(str(initial))
        if self.disabled:
            return initial
        print('bound data')
        print(str(data))
        return data
        
    def has_changed(self, initial, value):
        print('has changed')
        #return str(initial)== str(value)
        return super().has_changed(initial, value)

    def get_bound_field(self, form, field_name):
        # called
        print('get_bound_field')
        #print(str(form))
        return BoundField(form, self, field_name)

    def get_data(self):
        if self.show_fields:
            b = {}
            for obj in self.queryset:
                obj_data = {f: getattr(obj, f) for f in self.show_fields}
                b[getattr(obj, self.pk)] =(obj_data)
            self.widget.data = b
            #self.widget.model = self.model
            self.widget.can_add=self.can_add
            self.widget.can_change=self.can_change
            self.widget.can_delete=self.can_delete
            self.widget.can_view=self.can_view
        else:
            self.widget.data = {'pk': value}

