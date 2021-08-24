from django.db.models import (
    ForeignKey, 
    OneToOneField, 
    SET_NULL,
)
from django.core import checks
from image.models import AbstractImage

class ImageRelationFieldMixin():
    # Some common base material
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
        kwargs['related_name'] = kwargs.get('related_name', '+')           
        kwargs['on_delete'] = kwargs.get('on_delete', SET_NULL)  
        kwargs['blank'] = kwargs.get('blank', True) 
        kwargs['null'] = kwargs.get('null', True) 
        kwargs['to_field'] = None

        # original signature
        #super().__init__(to, on_delete, related_name, related_query_name,
        #         limit_choices_to, parent_link, to_field,
        #         db_constraint, **kwargs)
        super().__init__(to, related_query_name,
                 limit_choices_to, parent_link,
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

    auto_delete
        delete image model on deletion of a model with this field.
        Needs to be enabled in signals. Default True
    '''
    auto_delete = True

    def __init__(self, to, **kwargs):
        if ('auto_delete' in kwargs):
            self.auto_delete = kwargs['auto_delete']
        kwargs['on_delete'] = kwargs.get('on_delete', SET_NULL) 
        kwargs['blank'] = kwargs.get('blank', True) 
        kwargs['null'] = kwargs.get('null', True) 
        kwargs['related_name'] = kwargs.get('related_name', '+') 
        kwargs['to_field'] = None
        
        # original signature
        #super().__init__(to, on_delete, **kwargs)
        super().__init__(to, **kwargs)
        
    def check(self, **kwargs):
        #NB run after the core checks
        return [
            *super().check(**kwargs),
            *self._check_relation_model_is_image_model(),
            ]
