from django.db.models.signals import post_delete
from django.db import transaction
from image import settings
from image.models import Image, Reform
from image.decisions import src_should_delete



def _post_delete_src_delete(instance, **kwargs):
    if (src_should_delete(instance, False)):
        # Pass false so FileFields don't save the model.
        transaction.on_commit(lambda: instance.src.delete(False))
    

def register_signal_handlers():
    print('singals registered')
    post_delete.connect(_post_delete_src_delete, sender=Image)
    post_delete.connect(_post_delete_src_delete, sender=Reform)
