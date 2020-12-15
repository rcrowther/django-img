from contextlib import contextmanager
import os.path
from pathlib import Path
from collections import OrderedDict
from functools import partial
from django.db import models
from django.core.checks import Error, Warning
#from django.urls import reverse
from django.core.files.images import ImageFile
from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.apps import apps
from image import decisions
from image import utils
from image import checks
from image.model_fields import ImageFileField, ReformFileField
 
 

class SourceImageIOError(IOError):
    """
    Custom exception to distinguish IOErrors that were thrown while opening the source image
    """
    pass
    

def get_image_upload_to(instance, filename):
    """
    Obtain a valid upload path for an image file.
    This needs to be a module-level function so that it can be 
    referenced within migrations, but simply delegates to the 
    `get_upload_to` method of the instance, so that AbstractImage
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
    '''
    Data about stored images.
    
    Provides db fields for width, height, bytesize and upload_data. 
    These replace storage backend ingenuity with recorded data.
    Also provides accessors for useful derivatives such as 'alt' and 
    'url'.
    
    Handles upload_to in a configurable way, and also provides 
    machinery for Reform handling.
    
    A note on configuration. An Image or Reform is always expected to 
    point at a file, it is never null. To not point at a file is an 
    error---see shortcuts and 'broken image'. Whatever model keys an 
    Image/Reform is still free to be null.
    
    An Images/Reform model is locked to a file folder. New models, even 
    if given files from the same folder, are file-renamed by Django. 
    Thus each file is unique, and each file field in the model is 
    unique.  
    '''
    
    # Provides is a link for searching without Django's
    # relate machinery. It's safe as None.
    # Subclasses need to use a string name (Django 'Defered')
    reform_model = None

    # relative to MEDIA_ROOT
    upload_dir='originals'

    # 100 is Django default
    filepath_length=100
    
    # limit the unload filename length by checking on generateed forms.
    # (if false, all filenames are accepted then truncated if necessary)
    form_limit_filepath_length=True
    
    # List of formats accepted. Should be lower-case, short form.
    # If None, any format recognised as an image.
    accept_formats = None
    
    # If None, any size allowed. In MB. Real allowed.
    max_upload_size = 2
    
    auto_delete_files=False

    @classmethod
    def delete_file(cls, instance, **kwargs):
        transaction.on_commit(lambda: instance.src.delete(False))

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        if (cls.auto_delete_files):
            signals.post_delete.connect(cls.delete_file, sender=cls)
          
    upload_time = models.DateTimeField(_("Datetime of upload"),
        auto_now_add=True, editable=False
    )

    # A note about the name. Even if possible, using the word 'file'
    # triggers my, and probably other, IDEs. Again, even if possible,
    # naming this the same as the model is not a good idea, if only due 
    # to confusion in relations, let alone stray attribute manipulation 
    # in Python code. So, like HTML, it is 'src'     
    src = ImageFileField(_('image_file'), 
        unique=True,
        upload_to=get_image_upload_to, 
        width_field='width', 
        height_field='height',
        bytesize_field="bytesize",
    )
    
    # Django can use Pillow to provide width and height. So why?
    # The 'orrible duplication, which Django supports, is to spare web 
    # hits on remote storage, and opening and closing the file for data. 
    # Sure, the values could be cached, but here assuming code needs
    # a solid reecord.
    width = models.PositiveIntegerField(verbose_name=_('width'), editable=False)
    height = models.PositiveIntegerField(verbose_name=_('height'), editable=False)

    # Not autopoulated by storage, so funny name.
    # See the property
    bytesize = models.PositiveIntegerField(null=True, editable=False)

    @classmethod
    def get_reform_model(cls):
        """ Get the Reform models for this Image model """
        return apps.get_model(cls._meta.app_label, cls.reform_model)
        
    def is_local(self):
        """
        Is the image on a local filesystem?
        return
            True if the image is hosted on the local filesystem
        """
        try:
            self.src.path
            return True
        except ValueError as e:
            # The access attempt will fail with currently a ValueError
            # if no associated file. But in context of asking 'is it 
            # local?' that's now a source error.
            raise SourceImageIOError(str(e))
        except NotImplementedError:
            return False

    def get_upload_to(self, filename):
        # Incoming filename comes from upload machinery, and needs 
        # treatment. Also, path needs appending.
        
        # Quote stock local file implementation:
        # Return the given string converted to a string that can be used for a clean
        # filename. Remove leading and trailing spaces; convert other spaces to
        # underscores; and remove anything that is not an alphanumeric, dash,
        # underscore, or dot.
        #filename = self.src.field.storage.get_valid_name(filename)
        
        # Then respect settings, such as truncation, and relative path 
        # to storage base
        # image_save_path(field_file, upload_dir, filename)
        filename = decisions.image_save_path(self, filename)
        return filename
        
    @contextmanager
    def open_src(self):
        # Open file if it is closed
        close_src = False
        try:
            src = self.src

            if self.src.closed:
                # Reopen the file
                if self.is_local():
                    self.src.open('rb')
                else:
                    # Some external storage backends don't allow reopening
                    # the file. Get a fresh file instance. #1397
                    storage = self._meta.get_field('src').storage
                    src = storage.open(self.src.name, 'rb')

                close_src = True
        except IOError as e:
            # IOError comes from... an IO error. 
            # re-throw these as a SourceImageIOError
            # so that calling code
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


    def get_reform(self, filter_instance):
        ''' Generate a reform for this image.
        @ifilter instance of a filter, to generate the reform. 
        can be class, instance or text for registry???
        '''
        Reform = self.get_reform_model()

        try:
            reform = Reform.objects.get(
                image=self,
                filter_id=filter_instance.human_id(),
            )
        except Reform.DoesNotExist:
            # make a new, reformed image and record for Reform DB table
            # Open the file then produce a reformed image.
            model_args = {
                'file_format': Reform.file_format, 
                'jpeg_quality': Reform.jpeg_quality
            }
            with self.open_src() as fsrc:
                (reform_buff, iformat) = filter_instance.process(
                fsrc,
                model_args
                )

            # A destination filename. Code needed the filter's
            # decision on the extension.
            p = Path(self.src.name)
            #dst_fname = filter_instance.filename(p.stem, iformat)
            dst_fname = p.stem + '.' + iformat
            
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

    def get_filters_applied(self):
        '''Return all filter keys, so generated reforms, for this image.
        '''
        Reform = self.get_reform_model()
        return Reform.objects.filter(image=self).values_list('filter_id', flat=True)
        
    @property
    def filename(self):
        '''
        File as name, no path.
        Useful for admin displays, and others.
        '''
        return os.path.basename(self.src.name)

    @property
    def alt(self):
        '''
        String for an 'alt' field.
        The base implementation is derived from the filepath of the 
        uploaded file. 
        Subclasses might override this attribute to use more refined 
        data, such as a slug or title.
        '''
        return Path(self.src.name).stem + ' image'
                
    def is_portrait(self):
        return (self.width < self.height)

    def is_landscape(self):
        return (self.height < self.width)

    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        name = cls.__name__.lower()
        if not cls._meta.swapped:
            errors += [
            #NB By the time of check() models are built. So all 
            # attributes exist, at least as default.
            *checks.check_type('reform_model', cls.reform_model, str, '{}.E001'.format(name), **kwargs),
            #*checks.check_str('upload_dir', cls.upload_dir, 1, '{}.E002'.format(name), **kwargs),
            *checks.check_numeric_range('filepath_length', cls.filepath_length, 1, 65535, '{}.E003'.format(name), **kwargs),
            *checks.check_image_formats_or_none('accept_formats', cls.accept_formats,'{}.E004'.format(name), **kwargs),
            *checks.check_positive_float_or_none('max_upload_size', cls.max_upload_size, '{}.E003'.format(name), **kwargs),
            ]
        return errors
        
    def url_form_reform_add(self):
        '''URL to point at the reform add form.
        '''
        return '/admin/{}/{}/reforms/{}/add'.format(self._meta.app_label, self._meta.model_name, self.pk)

    @classmethod
    def url_view_form_reform_add(cls):        
        return 'admin/{}/{}/reforms/<int:pk>/add'.format(cls._meta.app_label, cls._meta.model_name)

    @classmethod
    def url_view_form_reform_add_name(cls):        
        return 'admin_{}_{}_reforms_add'.format(cls._meta.app_label, cls._meta.model_name)
        
    def __repr__(self):
        return "{}(upload_time: {}, src:'{}')".format(
            self.__class__.__name__,
            self.upload_time,
            self.src,
        )                

    def __str__(self):
        return self.src.name

    class Meta:
        abstract = True
        
        



from django.db import transaction
from django.db.models import signals



class AbstractReform(models.Model):
        
    @classmethod
    def delete_file(cls, instance, **kwargs):
        transaction.on_commit(lambda: instance.src.delete(False))
        
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__()
        signals.post_delete.connect(cls.delete_file, sender=cls)
              
    image_model = AbstractImage
    
    # relative to MEDIA_ROOT
    upload_dir='reforms'
    
    # Add the appname to the filename. This is good id, but
    # in practice makes long filenames e.g. 
    # site_images_thumbnail-washing_machine.png
    app_namespace = True

    # lowercase the filename. Default True.
    lowercase = True
    file_format = None
    jpeg_quality = 80
        
    # For naming, see the note in AbstractImage
    src = ReformFileField(
        unique=True,
        upload_to=get_reform_upload_to,
        )
    filter_id = models.CharField(max_length=255, db_index=True)


    @property
    def url(self):
        return self.src.url

    @property
    def alt(self):
        '''
        String for an 'alt' field.
        The base implementation is derived from the filepath. 
        Subclasses might override this attribute.
        '''
        #NB this could be lifted from the image, and is more consistent
        # like that. but it's a DB hit
        return Path(self.src.name).stem[:-(len(self.filter_id) + 1)] + ' image'
        
    @property
    def attrs_dict(self):
        """
        A dict of the src and alt attributes for html tags.
        """
        return OrderedDict([
            ('src', self.url),
            ('alt', self.alt),
        ])

    def get_upload_to(self, filename):
        # Incoming filename comes from get_reform() in Image, and  
        # only needs path appending.
        return decisions.reform_save_path(self, 
            filename, 
            self.app_namespace,
            self.lowercase
        )

    def delete(self, using=None, keep_parents=False):
        r = super().delete(using, keep_parents)
        self.src.delete(False)
        return r
        
    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        name = cls.__name__.lower()
        if not cls._meta.swapped:
            errors += [
            #NB By the time of check() models are built. So all 
            # attributes exist, at least as default.
            *checks.check_is_subclass('image_model', cls.image_model, AbstractImage, '{}.E001'.format(name), **kwargs),
            #*checks.check_str('upload_dir', cls.upload_dir, 1, '{}.E002'.format(name), **kwargs),
            *checks.check_image_format_or_none('file_format', cls.file_format, '{}.E002'.format(name), **kwargs),
            *checks.check_jpeg_legible(cls.jpeg_quality, '{}.W001'.format(name), **kwargs),
            ]
        return errors

    def __repr__(self):
        return "{}(image:'{}', src:'{}', filter_id:'{}')".format(
            self.__class__.__name__,
            self.image,
            self.src,
            self.filter_id,
        )
    
    def __str__(self):
        return self.src.name

        
    class Meta:
        abstract = True
