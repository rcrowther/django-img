from django.db import models
from django.db.models.signals import pre_delete, pre_save
import os.path

#x replace with image.settings
from django.conf import settings

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
#from willow.image import Image as WillowImage
#from PIL import Image as PILImage
#from image.filters import Filter
from image.utils import image_save_path, reform_filename, reform_save_path
#from image.settings import settings
print('create models')

#x
from io import BytesIO
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
        
    cdate = models.DateTimeField(_("Date of upload"),
        auto_now_add=True,
        db_index=True
    )
    title = models.CharField(_('title'),
        max_length=255,
    )
    ifile = models.ImageField(_('file'), 
        upload_to=get_upload_to, 
        width_field='width', 
        height_field='height'
    )
    
    #x
    # Django uses pillow anyway to provide width and height
    # can we autopopulate those from remote?
    width = models.PositiveIntegerField(verbose_name=_('width'), editable=False)
    height = models.PositiveIntegerField(verbose_name=_('height'), editable=False)
    #x 
    # I think the orrible duplication with ImageField.size is to cover remote loads?
    size = models.PositiveIntegerField(null=True, editable=False)


    def is_stored_locally(self):
        """
        Returns True if the image is hosted on the local filesystem
        """
        try:
            self.ifile.path

            return True
        except NotImplementedError:
            return False

            
    #? We have it or don't. Whats this for?
    # This exists because, although Django Imagefield will autopopulate 
    # width and height via Pillow, pillow will not find the filesize.
    # That can be done by opening a file using Python.
    #! get bytesize       
    def get_file_size(self):
        if self.size is None:
            try:
                self.size = self.ifile.size
            except Exception as e:
                # File not found
                #
                # Have to catch everything, because the exception
                # depends on the file subclass, and therefore the
                # storage being used.
                raise SourceImageIOError(str(e))

            self.save(update_fields=['size'])

        return self.size


    def get_upload_to(self, filename):
        print('image upload_to:')
        print(str(filename))
        # Incoming filename comes from upload machinery, and needs 
        # treatment. Also, path needs appending.
        #! replace with settings.media_subpath_originals
        folder_name = 'original_images'
        
        #  storage.get_valid_name():
        # Quote stock local file implementation:
        # Return the given string converted to a string that can be used for a clean
        # filename. Remove leading and trailing spaces; convert other spaces to
        # underscores; and remove anything that is not an alphanumeric, dash,
        # underscore, or dot.
        filename = self.ifile.field.storage.get_valid_name(filename)
        print('image upload_to:')
        print(str(filename))
        #! replace with image.file_utils.filename
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
    def open_file(self):
        # Open file if it is closed
        close_file = False
        try:
            image_file = self.ifile

            if self.ifile.closed:
                # Reopen the file
                if self.is_stored_locally():
                    self.ifile.open('rb')
                else:
                    # Some external storage backends don't allow reopening
                    # the file. Get a fresh file instance. #1397
                    storage = self._meta.get_field('file').storage
                    image_file = storage.open(self.ifile.name, 'rb')

                close_file = True
        except IOError as e:
            # re-throw this as a SourceImageIOError so that calling code can distinguish
            # these from IOErrors elsewhere in the process
            raise SourceImageIOError(str(e))

        # Seek to beginning
        image_file.seek(0)

        try:
            yield image_file
        finally:
            if close_file:
                image_file.close()

            
    @classmethod
    def get_reform_model(cls):
        """ Get the Reform models for this Image model """
        #return get_related_model(cls.reforms.related)
        return cls.reforms.rel.related_model





    def get_reform(self, filter_instance):
        '''ifilter can be class, instance or text for registry???
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
                filter_spec=filtername,
            )
        except Reform.DoesNotExist:
            # make a new, reformed image and record for Reform DB table            

            # First, a destination filename. The 
            # field settings will handle the path, but we need a filename.                
            # 'name' is path relative to media/. Name only, pleaee.
            #src_fname = os.path.basename(self.ifile.name)
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
                self.ifile.name,
                filter_instance, 
                iformat
            )
            
            # Right, lets make a Django ImageFile from that
            reform_file = ImageFile(reform_buff, name=dst_fname)
            
            # We got everything Django likes. A model save should 
            # generate a Reform DB entry and the file itself.
            reform = Reform(
                image = self,
                filter_spec = filter_instance.path_str(),
                ifile = reform_file,
                width = filter_instance.width,
                height = filter_instance.height,
            )
            reform.save()

        return reform


    def is_portrait(self):
        return (self.width < self.height)

    def is_landscape(self):
        return (self.height < self.width)
        
    @property
    def filename(self):
        return os.path.basename(self.ifile.name)
        
    @property
    def default_alt_text(self):
        # by default the alt text field (used in rich text insertion) is populated
        # from the title. Subclasses might provide a separate alt field, and
        # override this
        return self.title
        
    def img_tag(self, extra_attributes={}):
        '''return html for the original upload'''
        attrs = {'src': self.ifile.url, 'alt': self.default_alt_text}
        attrs.update(extra_attributes)
        return mark_safe('<img{}>'.format(flatatt(attrs)))
        
    def __str__(self):
        return self.title

    class Meta:
        abstract = True
        
        
        
class Image(AbstractImage):
    # admin_form_fields = (
        # 'title',
        # 'file',
        # 'collection',
        # 'tags',
        # 'focal_point_x',
        # 'focal_point_y',
        # 'focal_point_width',
        # 'focal_point_height',
    # )

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')


#x remove all
class Filter:
    """
    Represents one or more operations that can be applied to an Image to produce a reform
    appropriate for final display on the website. Usually this would be a resize operation,
    but could potentially involve colour processing, etc.
    """

    def __init__(self, spec=None):
        # The spec pattern is operation1-var1-var2|operation2-var1
        self.spec = spec

    @cached_property
    def operations(self):
        # Search for operations
        self._search_for_operations()

        # Build list of operation objects
        operations = []
        for op_spec in self.spec.split('|'):
            op_spec_parts = op_spec.split('-')

            if op_spec_parts[0] not in self._registered_operations:
                raise InvalidFilterSpecError("Unrecognised operation: %s" % op_spec_parts[0])

            op_class = self._registered_operations[op_spec_parts[0]]
            operations.append(op_class(*op_spec_parts))
        return operations

    def run(self, image, output):
        with image.get_willow_image() as willow:
            original_format = willow.format_name

            # Fix orientation of image
            willow = willow.auto_orient()

            env = {
                'original-format': original_format,
            }
            for operation in self.operations:
                willow = operation.run(willow, image, env) or willow

            # Find the output format to use
            if 'output-format' in env:
                # Developer specified an output format
                output_format = env['output-format']
            else:
                # Convert bmp and webp to png by default
                default_conversions = {
                    'bmp': 'png',
                    'webp': 'png',
                }

                # Convert unanimated GIFs to PNG as well
                if not willow.has_animation():
                    default_conversions['gif'] = 'png'

                # Allow the user to override the conversions
                conversion = getattr(settings, 'IMAGE_FORMAT_CONVERSIONS', {})
                default_conversions.update(conversion)

                # Get the converted output format falling back to the original
                output_format = default_conversions.get(
                    original_format, original_format)

            if output_format == 'jpeg':
                # Allow changing of JPEG compression quality
                if 'jpeg-quality' in env:
                    quality = env['jpeg-quality']
                elif hasattr(settings, 'IMAGE_JPEG_QUALITY'):
                    quality = settings.IMAGE_JPEG_QUALITY
                else:
                    quality = 85

                # If the image has an alpha channel, give it a white background
                if willow.has_alpha():
                    willow = willow.set_background_color_rgb((255, 255, 255))

                return willow.save_as_jpeg(output, quality=quality, progressive=True, optimize=True)
            elif output_format == 'png':
                return willow.save_as_png(output, optimize=True)
            elif output_format == 'gif':
                return willow.save_as_gif(output)
            elif output_format == 'webp':
                return willow.save_as_webp(output)

    def get_cache_key(self, image):
        vary_parts = []

        for operation in self.operations:
            for field in getattr(operation, 'vary_fields', []):
                value = getattr(image, field, '')
                vary_parts.append(str(value))

        vary_string = '-'.join(vary_parts)

        # Return blank string if there are no vary fields
        if not vary_string:
            return ''

        return hashlib.sha1(vary_string.encode('utf-8')).hexdigest()[:8]

    _registered_operations = None

    @classmethod
    def _search_for_operations(cls):
        if cls._registered_operations is not None:
            return

        operations = []
        for fn in hooks.get_hooks('register_image_operations'):
            operations.extend(fn())

        cls._registered_operations = dict(operations)


class AbstractReform(models.Model):
    #! change to filter_id
    filter_spec = models.CharField(max_length=255, db_index=True)
    ifile = models.ImageField(
        upload_to=get_reform_upload_to, 
        width_field='width', 
        height_field='height'
        )
    # get rid of these. You can use ifile.width
    # or not?
    width = models.IntegerField(editable=False)
    height = models.IntegerField(editable=False)
    #Should this not have a sbytesize then?
    
    @property
    def url(self):
        return self.ifile.url

    @property
    def alt(self):
        return self.image.title

    @property
    def attrs(self):
        """
        The src, width, height, and alt attributes for an <img> tag, as a HTML
        string
        """
        return flatatt(self.attrs_dict)

    @property
    def attrs_dict(self):
        """
        A dict of the src, width, height, and alt attributes for an <img> tag.
        """
        return OrderedDict([
            ('src', self.url),
            ('width', self.width),
            ('height', self.height),
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
        folder_name = 'reforms'
        filename = self.ifile.field.storage.get_valid_name(filename)
        # print('reform upload_to:')
        # print(str(filename))
        # return os.path.join(folder_name, filename)
        return reform_save_path(filename)
        
    @classmethod
    def check(cls, **kwargs):
        errors = super(AbstractReform, cls).check(**kwargs)
        if not cls._meta.abstract:
            if not any(
                #set(constraint) == set(['image', 'filter_spec', 'focal_point_key'])
                set(constraint) == set(['image', 'filter_spec'])
                for constraint in cls._meta.unique_together
            ):
                errors.append(
                    checks.Error(
                        "Custom reform model %r has an invalid unique_together setting" % cls,
                        hint="Custom reform models must include the constraint "
                        "('image', 'filter_spec') in their unique_together definition.",
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
        return "Reform(image:'{}', ifile:'{}', filter_spec:'{}', width={}, height={})".format(
            self.image,
            self.ifile,
            self.filter_spec,
            self.width,
            self.height,
        )
        return s
    
    def __str__(self):
        return self.ifile.name
         
    class Meta:
        unique_together = (
            ('image', 'filter_spec'),
        )

# Receive the pre_delete signal and delete the file associated with the model instance.
@receiver(pre_delete, sender=Reform)
def reform_delete(sender, instance, **kwargs):
    # Pass false so FileField doesn't save the model.
    instance.ifile.delete(False)
