from django.db.models.signals import post_delete
from django.db import transaction
from image import settings
from image.models import Image, Reform
#from image.decisions import src_should_delete


def _image_delete(instance, **kwargs):
    '''
    For use in models with foerign keys to image models.
    Enable this in the ready() function of app, 
    
    It can act on the field parameter auto_delete built in to 
    ImageRelationFieldMixin mixedins i,e, imag.model_fields.
    '''
    # find image fields
    #! maybe gather relevant fields on the meta. This is ugly.
    #! run  a check so drop the class test?
    b = []
    for f in instance._meta.fields:
        if (issubclass(f, ImageRelationFieldMixin) and f.auto_delete):
            f.delete(False)

def _image_src_delete(instance, **kwargs):
    if (instance._meta.model.auto_delete_files):
    #if (src_should_delete(instance, Image.AutoDelete.YES)):
        transaction.on_commit(lambda: instance.src.delete(False))

def _reform_src_delete(instance, **kwargs):
    transaction.on_commit(lambda: instance.src.delete(False))
    
def register_signal_handlers():
    print('singals registered')
    post_delete.connect(_image_src_delete, sender=Image, weak=False)
    post_delete.connect(_reform_src_delete, sender=Reform, weak=False )
