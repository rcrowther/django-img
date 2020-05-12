from django.db.models.signals import post_delete
from django.db import transaction
from image import settings
from image.models import Image, Reform
from image.decisions import src_should_delete



def _image_src_delete(instance, **kwargs):
    if (src_should_delete(instance, Image.DELETE_YES)):
        #print('delete is on!')
        # Pass false so FileFields don't save the model.
        #! I need more info. Documentation seems to insidt objects are 
        # gone, suggesting transactions are done. Yet some code shows
        # wraps in transaction code. Ok, that respects rollbacks.
        # It also was not working, and I mean not calling, in my rig.
        # The cause is not weak references.
        #transaction.on_commit(lambda: instance.src.delete(False))
        instance.src.delete(False)

def _reform_src_delete(instance, **kwargs):
    #print('delete reform src')
    #print(str(instance.__repr__()))
    #! I need more info. Documentation seems to insidt objects are 
    # gone, suggesting transactions are done. Yet some code shows
    # wraps in transaction code. Ok, that respects rollbacks.
    # It also was not working, and I mean not calling, in my rig.
    # The cause is not weak references.
    #transaction.on_commit(lambda: instance.src.delete(False))
    instance.src.delete(False)
    

def register_signal_handlers():
    print('singals registered')
    post_delete.connect(_image_src_delete, sender=Image, weak=False)
    post_delete.connect(_reform_src_delete, sender=Reform, weak=False )
