from django.db.models import OneToOneField
from image.models import AbstractImage
from django.core import checks
from django.db import models



class ImageSingleField(OneToOneField):
    '''
    A preconfigured model field for Images.
    This is a OneToOneField, so not suitable for referring to several 
    images e.g gallery use. Also, becaue OneToOneField, once it has an
    image no other model in that table can share the image 
    (unique=True). Mainly intended for images coupled to models e.g
    'Sales product' -> 'Product image'.
    Mild configuration to delete image if model is deleted, and
    not to be able to track the image back to the model (the model
    can find it's image, though). 
    '''
    on_delete=models.CASCADE,
    related_name='+'
        
    def check(self, **kwargs):
        # run after the core checks
        return [
            *super().check(**kwargs),
            *self._check_relation_model_is_image_model(),
            ]
            
    def _check_relation_model_is_image_model(self):
        # These checks are run in 'show migrations' and 'runmigrations'.
        # By this check, it has been checked the related model exists.
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
