from django.db import models
from django.db.models.signals import pre_delete, pre_save
import os.path

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
#from image.filters import Filter
from image.utils import (
    image_save_path, 
    reform_filename, 
    reform_save_path
)
#from django.conf import settings
#from image.settings import settings
print('create models')
from django.core.files.images import ImageFile
 
 
class SourceImageIOError(IOError):
    """
    Custom exception to distinguish IOErrors that were thrown while opening the source image
    """
    pass
    

def get_upload_to(instance, filename):
    """
    Obtain a valid upload path for an image file.
    This needs to be a module-level function so that it can be referenced within migrations,
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
        height_field='height'
    )
    
    auto_delete = models.PositiveSmallIntegerField(_("Delete uploaded files on item deletion"), 
        choices=DELETE_UNSET,
        default=DELETE_UNSET,
    )    

    # Django uses pillow anyway to provide width and height
    # I think the 'orrible duplication is for cloud storage, to spare
    # web hits.
    width = models.PositiveIntegerField(verbose_name=_('width'), editable=False)
    height = models.PositiveIntegerField(verbose_name=_('height'), editable=False)
    bytesize = models.PositiveIntegerField(null=True, editable=False)


    def is_stored_locally(self):
        """
        Returns True if the image is hosted on the local filesystem
        """
        try:
            self.src.path
            return True
            
        except NotImplementedError:
            return False

            
    #? We have it or don't. What's this for?
    # This exists because, although Django Imagefield will autopopulate 
    # width and height via Pillow, pillow will not find the filesize.
    # That can be done by opening a file using Python.
    def get_bytesize(self):
        if self.bytesize is None:
            try:
                self.bytesize = self.src.size
            except Exception as e:
                # File not found
                #
                # Have to catch everything, because the exception
                # depends on the file subclass, and therefore the
                # storage being used.
                raise SourceImageIOError(str(e))

            self.save(update_fields=['bytesize'])

        return self.bytesize


    def get_upload_to(self, filename):
        print('image upload_to:')
        print(str(filename))
        # Incoming filename comes from upload machinery, and needs 
        # treatment. Also, path needs appending.
        #! replace with settings.media_subpath_originals
        #folder_name = 'original_images'
        
        #  storage.get_valid_name():
        # Quote stock local file implementation:
        # Return the given string converted to a string that can be used for a clean
        # filename. Remove leading and trailing spaces; convert other spaces to
        # underscores; and remove anything that is not an alphanumeric, dash,
        # underscore, or dot.
        filename = self.src.field.storage.get_valid_name(filename)
        print('image upload_to:')
        print(str(filename))
        #! replace with src.file_utils.filename
        # do a unidecode in the filename and then replace non-ascii 
        # characters in filename with _ , to sidestep issues with filesystem encoding
        # filename = "".join((i if ord(i) < 128 else '_') for i in unidecode(filename))

        # # Truncate filename so it fits in the 100 character limit
        # # https://code.djangoproject.com/ticket/9893
        # full_path = os.path.join(folder_name, filename)
        # if len(full_path) >= 95:
            # chars_to_trim = len(full_path) - 94
            # prefix, extension = os.path.splitext(filename)
            # filename = prefix[:-chars_to_trim] + extension
            # full_path = os.path.join(folder_name, filename)

        filename = image_save_path(filename)
        #full_path = os.path.join(folder_name, filename)
        
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
            # re-throw this as a SourceImageIOError so that calling code can distinguish
            # these from IOErrors elsewhere in the process
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
        #! what if filter is none?
        #filtername = None
        #filter_instance = filter_instance
        #! registry?
        # if isinstance(ifilter, str):
            # filtername = ifilter
            # #filterinstance = make one from the name. But that means a registry?
            # #filter, created = Filter.objects.get_or_create(spec=filter)
        # elif isinstance(ifilter, Filter):
            # filter_instance = ifilter            
            # filtername = ifilter.path_str()
        # else:
            # filter_instance = ifilter()
            # filtername = filter_instance.path_str()
        filtername = filter_instance.path_str()
            
        #cache_key = filter.get_cache_key(self)
        Reform = self.get_reform_model()

        try:
            reform = self.reforms.get(
                filter_id=filtername,
            )
        except Reform.DoesNotExist:
            # make a new, reformed image and record for Reform DB table            

            # First, a destination filename. The 
            # field settings will handle the path, but we need a filename.                
            # 'name' is path relative to media/. Name only, pleaee.
            #src_fname = os.path.basename(self.src.name)
            #src_fname_no_extension, extension = os.path.splitext(src_fname)
            # <srcname> - <filtername> . <format> 
            # <srcname> - <filtername> is a near-unique key. Near enough.
            # dst_fname = "{}-{}.{}".format(
                # src_fname_no_extension,
                # filter_instance.human_path(),
                # reform_write_attrs['format']
            # )
            # <srcname> - <filtername> is a near-unique key. Near enough.
                        
            # Open the file then produce a reformed image.
            with self.open_file() as fsrc:
                (reform_buff, iformat) = filter_instance.process(fsrc)

            dst_fname = reform_filename( 
                self.src.name,
                filter_instance, 
                iformat
            )
            
            # Right, lets make a Django ImageFile from that
            reform_file = ImageFile(reform_buff, name=dst_fname)
            
            # We got everything Django likes. A model save should 
            # generate a Reform DB entry and the file itself.
            reform = Reform(
                reform = reform_file,
                filter_id = filter_instance.path_str(),
                src = self,
                #! can't guarentee these, can we? unless preset in filter?
                #? needed at all?
                #width = filter_instance.width,
                #height = filter_instance.height,
                #width = 0,
                #height = 0,
            )
            reform.save()

        return reform


    def is_portrait(self):
        return (self.width < self.height)

    def is_landscape(self):
        return (self.height < self.width)
        
    @property
    def filename(self):
        return os.path.basename(self.src.name)
        
    @property
    def default_alt_text(self):
        # by default the alt text field is populated from the title. 
        # Subclasses might provide a separate alt field, and
        # override this
        return self.title
        
    #? Not convinved about having this here.
    def img_tag(self, extra_attributes={}):
        '''@return html for the original upload'''
        attrs = {'src': self.src.url, 'alt': self.default_alt_text}
        attrs.update(extra_attributes)
        return mark_safe('<img{}>'.format(flatatt(attrs)))

    def __repr__(self):
        return "Reform(upload_date: {}, title:'{}', src:'{}')".format(
            self.upload_date,
            self.title,
            self.src,
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
        #width_field='width', 
        #height_field='height'
        )
    filter_id = models.CharField(max_length=255, db_index=True)
    # get rid of these. You can use src.width
    # or not? Never used them.
    #width = models.IntegerField(editable=False)
    #height = models.IntegerField(editable=False)
    #Should this not have a sbytesize then?
    
    @property
    def url(self):
        return self.src.url

    @property
    def alt(self):
        return self.src.title

    @property
    def attrs(self):
        """
        The src and alt attributes for an <img> tag, as a HTML
        string
        """
        return flatatt(self.attrs_dict)

    @property
    def attrs_dict(self):
        """
        A dict of the src and alt attributes for an <img> tag.
        """
        return OrderedDict([
            ('src', self.url),
            ('alt', self.alt),
        ])

    def img_tag(self, extra_attributes={}):
        attrs = self.attrs_dict.copy()
        attrs.update(extra_attributes)
        return mark_safe('<img{}>'.format(flatatt(attrs)))

    def __html__(self):
        return self.img_tag()

    def get_upload_to(self, filename):
        # Incoming filename comes from get_reform() in Image, and  
        # only needs path appending.
        print('reform upload_to:')
        print(str(filename))
        #folder_name = 'reforms'
        filename = self.src.field.storage.get_valid_name(filename)
        # print('reform upload_to:')
        # print(str(filename))
        # return os.path.join(folder_name, filename)
        return reform_save_path(filename)
        
    @classmethod
    def check(cls, **kwargs):
        errors = super(AbstractReform, cls).check(**kwargs)
        if not cls._meta.abstract:
            if not any(
                #set(constraint) == set(['src', 'filter_idc', 'focal_point_key'])
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
    src = models.ForeignKey(Image, related_name='reforms', on_delete=models.CASCADE)

    def __repr__(self):
        return "Reform(image:'{}', src:'{}', filter_id:'{}')".format(
            self.image,
            self.src,
            self.filter_id,
        )
    
    def __str__(self):
        # Source name includes filter id, so not bad?
        #? or ???-self.filter.id_str_short()
        return self.src.name
         
         
    class Meta:
        unique_together = (
            ('src', 'filter_id'),
        )

