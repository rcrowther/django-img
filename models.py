from contextlib import contextmanager
import os.path
from pathlib import Path
from collections import OrderedDict

from django.db import models
from django.db.models.signals import pre_delete, pre_save

from django.utils.translation import gettext_lazy as _
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
#from django.dispatch.dispatcher import receiver
#from unidecode import unidecode
#from django.forms.utils import flatatt
from django.urls import reverse
from django.core.files.images import ImageFile
from image import decisions
from image.validators import validate_file_size, validate_image_file_extension
from django.core import checks

print('create models')
 
 
 
class SourceImageIOError(IOError):
    """
    Custom exception to distinguish IOErrors that were thrown while opening the source image
    """
    pass
    

def get_upload_to(instance, filename):
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


from image.model_fields import FreeImageField
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
    # None is 'use settings default'
    upload_dir='originals'
    
    # 100 is Django default
    #! template tag
    filepath_length=100
        
    class AutoDelete(models.IntegerChoices):
        UNSET = 0, _('Unset')
        NO = 1, _('Dont delete file')
        YES = 2, _('Auto-delete file')        
        

    # Not autopoulated by storage, so funny name.
    # See the property
    _upload_time = models.DateTimeField(_("Datetime of upload"),
        null=True, editable=False
    )

    @property
    def upload_time(self):
        '''
        upload time of the associated image.
        Cached in a database field.
        '''
        # Although Django Imagefield will autopopulate 
        # width and height, there is no support for upload_time.
        if self._upload_time is None:
            try:
                # Storage should handle file opening or web hits.
                self._upload_time = self.src.storage.get_created_time(self.src.name)
            except Exception as e:
                # File not found
                #
                # Have to catch everything, because the exception
                # depends on the storage being used.
                raise SourceImageIOError(str(e))

            self.save(update_fields=['_upload_time'])
        return self._upload_time

    #! not sure that title should be required, even with
    #! prepopulates. And it ain't unique. But what about
    #! the search issue? 
    # title = models.CharField(_('title'),
        # max_length=255,
        # #unique=True, 
        # db_index=True
    # )
    
    # A note about the name. Even if possible, using the word 'file'
    # triggers my, and probably other, IDEs. Again, even if possible,
    # naming this the same as the model is not a good idea, if only due 
    # to confusion in relations, let alone stray attribute manipulation 
    # in Python code. So, like HTML, it is 'src'     
    src = FreeImageField(_('image_file'), 
    #src = models.ImageField(_('image_file'), 
        unique=True,
        upload_to=get_upload_to, 
        width_field='width', 
        height_field='height',
        #storage=FileSystemStorage(l
        #    location=self.media_relative_path
        #),
        max_length=filepath_length, 
        #! model validators do not only run on upload, they run on any modification?
        # too much?
        validators = [
            validate_file_size,
            validate_image_file_extension
        ],
    )
    
    auto_delete = models.PositiveSmallIntegerField(_("Delete uploaded files on item deletion"), 
        choices=AutoDelete.choices,
        default=AutoDelete.UNSET,
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
    _bytesize = models.PositiveIntegerField(null=True, editable=False)

    @property
    def bytesize(self):
        '''
        vysize of the associated image.
        Cached in a database field.
        '''
        # Although Django Imagefield will autopopulate 
        # width and height, there is no support for bytesize.
        if self._bytesize is None:
            try:
                # Storage should handle file opening or web hits.
                self._bytesize = self.src.size
            except Exception as e:
                # File not found
                #
                # Have to catch everything, because the exception
                # depends on the storage being used.
                raise SourceImageIOError(str(e))

            self.save(update_fields=['_bytesize'])
        return self._bytesize

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
        print('model fielname:')
        print(str(filename))
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

            # A destination filename. Code needs the filter's
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
        
    #? move checks out of class
    #! needs to check media path
    @classmethod
    def _check_available_filelength(cls, **kwargs):
        '''
        Does filepath_length allow for filenames?
        '''
        errors = []
        declared_len = int(cls.filepath_length)
        path_len =  len(cls.upload_dir)
        if (declared_len <= path_len):
            errors.append(
                checks.Error(
                    "'filepath_length' must exceed base path length. 'filepath_length' len: {}, 'upload_dir' len: {}".format(
                     declared_len,
                     path_len,
                     ),
                    id='image_model.E002',
                )
            )
        elif (declared_len <= (path_len + 12)):
            errors.append(
                checks.Warning(
                    "Less than 12 chars avaiable for filenames. 'filepath_length' len: {}, 'upload_dir' len: {}".format(
                     declared_len,
                     path_len,
                     ),
                    id='image_model.W001',
                )
            )
        return errors
            
    @classmethod
    def _check_image_attrs(cls, **kwargs):
        '''
        Check filepath_length in a reasonable (modern OS) range.
        '''
        errors = []

        try:
            l = int(cls.filepath_length)
            if (l < 0 or l > 65000):
                raise ValueError()
        except (ValueError, TypeError):
            errors.append(
                checks.Error(
                    "'filepath_length' value '%s' must be a number > 0 and < 65000." % cls.filepath_length,
                    id='image_model.E001',
                )
            )
        return errors
        
    @classmethod
    def check(cls, **kwargs):
        errors = super().check(**kwargs)
        if not cls._meta.swapped:
            errors += [*cls._check_image_attrs(**kwargs)]
            errors += [*cls._check_available_filelength(**kwargs)]
        return errors
        
    def __repr__(self):
        return "Image(upload_time: {}, src:'{}', auto_delete:{})".format(
            #self.upload_date,
            self.upload_time,
            #self.title,
            self.src,
            self.auto_delete
        )                

    def __str__(self):
        return self.src.name

    class Meta:
        abstract = True
        
        
        
class Image(AbstractImage):

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')
        indexes = [
            models.Index(fields=['_upload_time']),
        ]
        # constraints = [
            # models.UniqueConstraint(fields=['src'], name='unique_image_image_src') 
        # ]



class AbstractReform(models.Model):
    # None is 'use settings default'
    upload_dir='reforms'

    # 100 is Django default
    filepath_length=100
    
    # For naming, see the note in AbstractImage
    src = models.FileField(
        unique=True,
        upload_to=get_reform_upload_to,
        )
    filter_id = models.CharField(max_length=255, db_index=True)
    
    @property
    def url(self):
        return self.src.url

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
            ('alt', self.alt),
        ])

    def get_upload_to(self, filename):
        # Incoming filename comes from get_reform() in Image, and  
        # only needs path appending.
        #filename = self.src.field.storage.get_valid_name(filename)

        # Then respect settings, such as truncation, and relative path 
         # to storage base
        #filename = decisions.image_save_path(self.src, self.upload_dir, filename)
        return decisions.reform_save_path(self, filename)
        
    # @classmethod
    # def check(cls, **kwargs):
        # errors = super(AbstractReform, cls).check(**kwargs)
        # if not cls._meta.abstract:
            # if not any(
                # set(constraint) == set(['src', 'filter_id'])
                # for constraint in cls._meta.unique_together
            # ):
                # errors.append(
                    # checks.Error(
                        # "Custom reform model %r has an invalid unique_together setting" % cls,
                        # hint="Custom reform models must include the constraint "
                        # "('src', 'filter_id') in their unique_together definition.",
                        # obj=cls,
                        # id='images.E001',
                    # )
                # )

        # return errors
  
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
        return self.src.name
         

    class Meta:
        verbose_name = _('reform')
        verbose_name_plural = _('reforms')
        # indexes = [
            # models.Index(fields=['src']),
        # ]
        # constraints = [
            # models.UniqueConstraint(fields=['src'], name='unique_image_reform_src') 
        # ]
