from django.db import models
from django.db.models.signals import pre_delete, pre_save
import os.path
from pathlib import Path

from contextlib import contextmanager
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.dispatch.dispatcher import receiver
from unidecode import unidecode
from django.forms.utils import flatatt
from django.urls import reverse
from collections import OrderedDict
from django.utils.functional import cached_property
from django.core.files.images import ImageFile
#from image.filters import Filter
from image.decisions import (
    image_save_path, 
    reform_save_path
)
#from image.settings import settings
print('create models')
from image.validators import validate_file_size, validate_image_file_extension
 
 
 
class SourceImageIOError(IOError):
    """
    Custom exception to distinguish IOErrors that were thrown while opening the source image
    """
    pass
    

def get_upload_to(instance, filename):
    """
    Obtain a valid upload path for an image file.
    This needs to be a moduget_reform_upload_tole-level function so that it can be referenced within migrations,
    but simply delegates to the `get_upload_to` method of the instance, so that AbstractImage
    subclasses can override it.
    """
    return instance.get_upload_to(filename)
    
    
def get_reform_upload_to(instance, filename):
    """
    Obtain a valid upload path for an image reform file.
    This needs to be a module-level function so that it can be referenced within migrations,
    but simply delegates to the `get_upload_to` method of the instance, so that AbstractReform
    subclasses can override it.
    """
    return instance.get_upload_to(filename)



class AbstractImage(models.Model):
    # Delete policy
    DELETE_UNSET = 0
    DELETE_NO = 1
    DELETE_YES = 2
    DELETE_POLICIES = [
        (DELETE_UNSET, 'None'),
        (DELETE_NO, 'No'),
        (DELETE_YES, 'Yes'),
    ]
    delete_policies = {
        DELETE_UNSET: None,
        DELETE_NO: False,
        DELETE_YES: True,
    }

    upload_date = models.DateTimeField(_("Date of upload"),
        auto_now_add=True,
        db_index=True
    )
    
    title = models.CharField(_('title'),
        max_length=255,
    )
    
    # A note about the name. Even if possible, using the word 'file'
    # triggers my, and probably other, IDEs. Again, even if possible,
    # naming this the same as the model is not a good idea, if only due 
    # to confusion in relations, let alone stray attribute manipulation 
    # in Python code. So, like HTML, it is 'src' 
    src = models.ImageField(_('image_file'), 
        upload_to=get_upload_to, 
        width_field='width', 
        height_field='height',
        validators = [
            validate_file_size,
            validate_image_file_extension
        ]
    )
    
    auto_delete = models.PositiveSmallIntegerField(_("Delete uploaded files on item deletion"), 
        choices=DELETE_POLICIES,
        default=DELETE_UNSET,
    )    

    # Django uses Pillow anyway to provide width and height. So why?
    # The 'orrible duplication is for cloud storage, to spare web hits. 
    # Also to stop opening and closing the file, which is how file 
    # storage attributes are loaded. Sure, they will be cached, but 
    # let's get this sorted here.
    width = models.PositiveIntegerField(verbose_name=_('width'), editable=False)
    height = models.PositiveIntegerField(verbose_name=_('height'), editable=False)

    # Not autopoulated by the storage, so funny name.
    # See the property further down.
    _bytesize = models.PositiveIntegerField(null=True, editable=False)


    def is_stored_locally(self):
        """
        Returns True if the image is hosted on the local filesystem
        """
        try:
            self.src.path
            return True
            
        except NotImplementedError:
            return False

    #! @property
    #! auto_delete and private
    def is_auto_delete(self):
        if (self.auto_delete == self.DELETE_NO):
            return False
        elif (self.auto_delete == self.DELETE_YES): 
            return True
        else:
            return None

    # This exists because, although Django Imagefield will autopopulate 
    # width and height via Pillow, pillow will not find the filesize.
    # That can be done by opening a file using Python.
    #! cache
    @property
    def bytesize(self):
        if self._bytesize is None:
            try:
                self._bytesize = self.src.size
            except Exception as e:
                # File not found
                #
                # Have to catch everything, because the exception
                # depends on the file subclass, and therefore the
                # storage being used.
                raise SourceImageIOError(str(e))

            self.save(update_fields=['_bytesize'])

        return self._bytesize


    def get_upload_to(self, filename):
        # Incoming filename comes from upload machinery, and needs 
        # treatment. Also, path needs appending.
        
        # Quote stock local file implementation:
        # Return the given string converted to a string that can be used for a clean
        # filename. Remove leading and trailing spaces; convert other spaces to
        # underscores; and remove anything that is not an alphanumeric, dash,
        # underscore, or dot.
        filename = self.src.field.storage.get_valid_name(filename)
        
        # truncate and makee relative to storage base
        filename = image_save_path(filename)
       
        return filename
        
        
    @contextmanager
    def open_src(self):
        # Open file if it is closed
        close_src = False
        try:
            src = self.src

            if self.src.closed:
                # Reopen the file
                if self.is_stored_locally():
                    self.src.open('rb')
                else:
                    # Some external storage backends don't allow reopening
                    # the file. Get a fresh file instance. #1397
                    storage = self._meta.get_field('src').storage
                    src = storage.open(self.src.name, 'rb')

                close_src = True
        except IOError as e:
            # re-throw this as a SourceImageIOError so that calling code
            # can distinguish these from IOErrors elsewhere in the 
            # process e.g. currently causes a broken-image display.
            raise SourceImageIOError(str(e))

        # Seek to beginning
        src.seek(0)

        try:
            yield src
        finally:
            if close_src:
                src.close()

    #? unused except for search eror handling
    @classmethod
    def get_reform_model(cls):
        """ Get the Reform models for this Image model """
        #return get_related_model(cls.reforms.related)
        return cls.reforms.rel.related_model


    def get_reform(self, filter_instance):
        ''' Generate a reform for this image.
        @ifilter instance of a filter, to generate the reform. 
        can be class, instance or text for registry???
        '''
        Reform = self.get_reform_model()

        try:
            reform = self.reforms.get(
                filter_id=filter_instance.human_id(),
            )
        except Reform.DoesNotExist:
            # make a new, reformed image and record for Reform DB table
            # Open the file then produce a reformed image.
            with self.open_src() as fsrc:
                (reform_buff, iformat) = filter_instance.process(fsrc)

            # A destination filename. Code needed the filter's
            # decision on the extension.
            p = Path(self.src.name)
            dst_fname = filter_instance.filename(p.stem, iformat)
            
            # Right, lets make a Django ImageFile from that
            reform_file = ImageFile(reform_buff, name=dst_fname)
            
            # We got everything Django likes. A model save should 
            # generate a Reform DB entry and the file itself.
            reform = Reform(
                image = self,
                filter_id = filter_instance.human_id(),
                src = reform_file,
            )

            reform.save()

        return reform


    def is_portrait(self):
        return (self.width < self.height)

    def is_landscape(self):
        return (self.height < self.width)
    #x another what for?
    @property
    def filename(self):
        return os.path.basename(self.src.name)
        
    @property
    def alt(self):
        # The model has no 'alt' field 
        # Default alt attribute is 
        # title.lower() + ' image'. 
        # Subclasses might  provide a field, override this attribute, 
        # or manipilate template contexts.
        return self.title.lower() + ' image'

    def __repr__(self):
        return "Reform(upload_date: {}, title:'{}', src:'{}', auto_delete:{})".format(
            self.upload_date,
            self.title,
            self.src,
            self.auto_delete
        )                

    def __str__(self):
        return self.title

    class Meta:
        abstract = True
        
        
        
class Image(AbstractImage):

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')



class AbstractReform(models.Model):
    # For naming, see the note in AbstractImage
    src = models.FileField(
        upload_to=get_reform_upload_to,
        )
    filter_id = models.CharField(max_length=255, db_index=True)
    
    @property
    def url(self):
        return self.src.url

    #! cache against lookup?
    @property
    def alt(self):
        return self.image.alt

    @property
    def attrs_dict(self):
        """
        A dict of the src and alt attributes for html tags.
        """
        return OrderedDict([
            ('src', self.url),
         #   ('src', self.src.name),
            ('alt', self.alt),
        ])

    def get_upload_to(self, filename):
        # Incoming filename comes from get_reform() in Image, and  
        # only needs path appending.
        filename = self.src.field.storage.get_valid_name(filename)

        return reform_save_path(filename)
        
    @classmethod
    def check(cls, **kwargs):
        errors = super(AbstractReform, cls).check(**kwargs)
        if not cls._meta.abstract:
            if not any(
                set(constraint) == set(['src', 'filter_id'])
                for constraint in cls._meta.unique_together
            ):
                errors.append(
                    checks.Error(
                        "Custom reform model %r has an invalid unique_together setting" % cls,
                        hint="Custom reform models must include the constraint "
                        "('src', 'filter_id') in their unique_together definition.",
                        obj=cls,
                        id='images.E001',
                    )
                )

        return errors
  
    class Meta:
        abstract = True



class Reform(AbstractReform):
    image = models.ForeignKey(Image, related_name='reforms', on_delete=models.CASCADE)

    def __repr__(self):
        return "Reform(image:'{}', src:'{}', filter_id:'{}')".format(
            self.image,
            self.src,
            self.filter_id,
        )
    
    def __str__(self):
        # Source name includes filter id, so unique
        return self.src.name
         
         
    class Meta:
        unique_together = (
            ('src', 'filter_id'),
        )

