from django.db.models.signals import post_delete
from django.db import transaction
from image import settings
from image.models import Image, Reform
from image.decisions import src_should_delete



def _image_src_delete(instance, **kwargs):
    if (src_should_delete(instance, Image.AutoDelete.YES)):
        transaction.on_commit(lambda: instance.src.delete(False))

def _reform_src_delete(instance, **kwargs):
    transaction.on_commit(lambda: instance.src.delete(False))
    

def register_signal_handlers():
    print('singals registered')
    post_delete.connect(_image_src_delete, sender=Image, weak=False)
    post_delete.connect(_reform_src_delete, sender=Reform, weak=False )
