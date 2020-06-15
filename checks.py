from itertools import chain

from django.core import checks
from django.contrib.admin.checks import BaseModelAdminChecks
from django.forms import BaseForm
from django.core.exceptions import FieldDoesNotExist
from django.contrib.admin import checks as admincheck
from django.db import models
from inspect import isclass



class InlineForwardsModelAdminChecks(BaseModelAdminChecks):

    def check(self, admin_obj, **kwargs):
        #print('check forwards inline')
        self._check_fi_keys_unique(admin_obj)
        #print(str(admin_obj))
        return [
            *self._check_fi_fields(admin_obj),
        ]

    def _check_fi_keys_unique(self, obj):
        #print('check forwards inline')
        #self._check_fi_keys_unique(admin_obj)
        #print(str(obj))
        keys =  obj.inline_forwards.keys()
        for k in keys:
            k_str = k
            if isclass(k_str):
                k_str = k_str.__name__ 
            if k_str in keys:
                return [
                    checks.Error(
                        "The value of '%s' as a string clashes with "
                        "another key." % (
                            k_str
                        ),
                        obj=obj.__class__,
                        id='admin.E023',
                    )]    
                                
    def _check_fi_fields(self, obj):
        """ Check that `inline_forwards` is a dictionary. """
        if not isinstance(obj.inline_forwards, dict):
            return admincheck.must_be('a dictionary', option='inline_forwards', obj=obj, id='admin.E021')
        else:
            #r = self._check_fi_keys_unique(obj.inline_forwards)
            #if r:
            #    return r
            #else:
                return list(chain.from_iterable(
                    self._check_fi_fields_key(obj, field_name, 'inline_forwards') +
                    self._check_fi_fields_value(obj, val, 'inline_forwards["%s"]' % field_name) 
                    for field_name, val in obj.inline_forwards.items()
                ))

    def _check_fi_fields_key(self, obj, field_name, label):
        """ Check that a key of `inline_forwards` dictionary is name of existing
        field and that the field is a ForeignKey. """

        try:
            field = obj.model._meta.get_field(field_name)
        except FieldDoesNotExist:
            return admincheck.refer_to_missing_field(field=field_name, option=label, obj=obj, id='admin.E022')
        else:
            if (not (isinstance(field, models.ForeignKey))):
                return [
                    checks.Error(
                        "The value of '%s' refers to '%s', which is not an "
                        "instance of ForeignKey." % (
                            label, field_name
                        ),
                        obj=obj.__class__,
                        id='admin.E023',
                    )
                ]
            else:
                return []

        

    def _check_fi_fields_value(self, obj, val, label):
        """ Check value of `inline_forwards` dictionary is a class based in BaseModelAdmin. """

        import inspect
        from django.contrib.admin.options import BaseModelAdmin

        if (not(inspect.isclass(val))):            
            return [
                checks.Error(
                    "The value of '%s' must be a class inheriting from BaseModelAdmin." % (label),
                    obj=obj.__class__,
                    id='admin.E024',
                )
            ]
        else:
            print(str(val))
            if (issubclass(val, BaseModelAdmin) or issubclass(val, BaseForm)):
                return []
            else:
                return admincheck.must_inherit_from(parent='BaseModelAdmin or Form', option=val, obj=obj, id='admin.E206')




