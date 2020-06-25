from django.db.models import ForeignKey, OneToOneField, ImageField
from django.core import checks
from django.db import models

#from  django.db.models.fields.mixins import FieldCacheMixin
#from django.utils.functional import cached_property
from image import form_fields



class FreePathImageField(ImageField):
    '''
    A (model) ImageField that defaults to returning a (form) 
    FreePathImageField.
    FreePathImageField allows on input any length of file path.
    '''
    # This class exists because I can find no way of overriding this 
    # default on declaration.
    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': form_fields.FreePathImageField,
            'max_length': self.max_length,
            **kwargs,
        })

        

class ImageRelationFieldMixin():
    auto_delete = False
    
    def _check_relation_model_is_image_model(self):
        # These checks are run in 'show migrations' and 'runmigrations'.
        # By this check, the related model must exist.
        remote_class = self.remote_field.model

        # ...but that attribute may be by lazy string, which means
        # rooting about for a model class
        rel_is_string = isinstance(remote_class, str)
        if (rel_is_string):
            remote_class = self.opts.apps.all_models[remote_class]

        if (not(issubclass(remote_class, AbstractImage))):
            # More rooting about. Fun, huh? 
            model_name = self.remote_field.model if rel_is_string else self.remote_field.model._meta.object_name
            return [
                checks.Error(
                    "ImageSingleField defines a relation with model '%s', which is "
                    "not a subclass of AbstractImage." % model_name,
                    obj=self,
                    id='fields.E300',
                )
            ]
        return []



class ImageManyToOneField(ImageRelationFieldMixin, ForeignKey):
    '''
    A preconfigured ManyToOne model field for Images.

    This is a ForeignKey, so several models can refer to one image.
    It is suitable for referring to images intended as a pool e.g. 
    for gallery use.
    
    The field has some dafaults, which can be overridden,
    - The field is nullable
    - Deletion of the image sets the field to null
    - Deletion of the model will not delete the image 
    - The image can not refer back to the model
    '''
    def __init__(self, to, related_query_name=None,
                 limit_choices_to=None, parent_link=False,
                 db_constraint=True, **kwargs):
        if ('auto_delete' in kwargs):
            self.auto_delete = kwargs['auto_delete']

        # not kwrd, set a default
        on_delete = kwargs.get('on_delete', models.SET_NULL)
        kwargs['blank'] = kwargs.get('blank', True) 
        kwargs['null'] = kwargs.get('null', True) 
        related_name = kwargs.get('related_name', '+')           
        to_field = None
        super().__init__(to, on_delete, related_name, related_query_name,
                 limit_choices_to, parent_link, to_field,
                 db_constraint, **kwargs)
                         
    def check(self, **kwargs):
        #NB run after the core checks
        return [
            *super().check(**kwargs),
            *self._check_relation_model_is_image_model(),
            ]
            
            
            

class ImageOneToOneField(ImageRelationFieldMixin, OneToOneField):
    '''
    A preconfigured OneToOne model field for Images.
    
    This is a OneToOneField, so suitable when the model containing the 
    field is locked to one image (which other models can not use) e.g.
    'Sales product' -> 'Product image'.

    The field has some dafaults, which can be overridden,
    - The field is nullable
    - Deletion of the image sets the field to null
    - Deletion of the model deletes the image 
    - The image can not refer back to the model
    '''
    auto_delete = True

    def __init__(self, to, **kwargs):
        if ('auto_delete' in kwargs):
            self.auto_delete = kwargs['auto_delete']
            
        # not kwrd, set a default
        on_delete = kwargs.get('on_delete', models.SET_NULL)
        kwargs['blank'] = kwargs.get('blank', True) 
        kwargs['null'] = kwargs.get('null', True) 
        kwargs['related_name'] = kwargs.get('related_name', '+') 
        kwargs['to_field'] = None
        super().__init__(to, on_delete, **kwargs)
        
    def check(self, **kwargs):
        #NB run after the core checks
        return [
            *super().check(**kwargs),
            *self._check_relation_model_is_image_model(),
            ]
