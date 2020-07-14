from django.db.models.signals import post_delete
from django.db import transaction
from django.core.exceptions import ValidationError
from image.model_fields import ImageOneToOneField

def _image_delete(instance, **kwargs):
    '''
    For use in models with foreign keys to image models.
    Enable this in the ready() function of app, 
    
    It can act on the field parameter auto_delete built in to 
    ImageRelationFieldMixin mixedins i,e, imag.model_fields.
    '''
    # find image fields
    #? ugly, but...?
    b = []
    for f in instance._meta.fields:
        if (issubclass(f, ImageOneToOneField) and f.auto_delete):
            f.delete(False)

def register_image_delete_handler(model):
    post_delete.connect(_image_delete, sender=model, weak=False)

def _image_src_delete(instance, **kwargs):
    transaction.on_commit(lambda: instance.src.delete(False))

def _reform_src_delete(instance, **kwargs):
    transaction.on_commit(lambda: instance.src.delete(False))

def register_reform_delete_handler(reform_class):   
    post_delete.connect(_reform_src_delete, sender=reform_class, weak=False )

def register_file_delete_handler(image_class, reform_class):
    post_delete.connect(_image_src_delete, sender=image_class, weak=False)
    post_delete.connect(_reform_src_delete, sender=reform_class, weak=False )
