from PIL import Image as PILImage
from io import BytesIO
from image.utils import ModulePath
from pathlib import Path
from image import image_processes
from image.settings import settings, check_jpeg_quality, check_image_formats
#x IMAGE_FORMATS
from image.constants import IMAGE_FORMATS, FORMAT_APP_PILLOW, FORMAT_PILLOW_APP
print('create filters')

        
class Filter():
    '''
    A filter defines how to transorm a image with a spec into 
    a derivative with a different spec.
    As such, it is more than a static configuration. It is half-
    functional. takes an open Python file and returns a buffer. 
    The stock implementation uses Pillow, but this setup allows 
    other codebases to bue used in a filler without changing calling 
    code.
    '''
    #def __new__(cls, *args, **kwargs):
        # print('called Filter new')
        # print(str(cls))
        # print(str(dir(cls)))
        # print(str(dir(cls.__class__)))
        # print(str(args))
        # print(str(kwargs))
        #cls.testAttrNotFalse()
        #return super().__new__(cls, *args, **kwargs)


    @classmethod
    def testAttrNotFalse(cls, *args):
        nulled = [k for k in args if (not(getattr(cls, k)))]
        if (len(nulled) > 0):
            raise ValueError("Attribute(s) not set or None: class '{}': attr: {}".format(
                cls.__name__, 
                "'" + "', '".join(nulled) + "'")
            )           

    
    def path_str(self):
        '''
        Return thhe dotted module and classname as a string.
        
        Should be unique, and work as an id for the class. Moreover, it 
        should persist across code versions.
        '''
        return self.__module__ + '.' + type(self).__name__
    
        
    #! cached property?
    def id_str_short(self):
        '''
        Id for a filter, usable for keys.
        This is not guarenteed unique. It depends on the filter being
        placed in unique module packages. Which, in Django, they
        would be, inside app names.
        Currently formed as <module parent> + '_' + <filtername> 
        '''
        p = ModulePath.from_str(self.__module__)
        
        # protect against no module path. 'image_filters' namespacing
        # seems pointless
        if (p.size < 2):
            return type(self).__name__.lower()

        # Take the second-last element. The leaf element in the 
        # surrounding system is always 'image_file', which is generic, 
        # but the parent element is distinctive, often an appname, so 
        # useful.                  
        s = p.branch.leaf.str + '_' + type(self).__name__
        
        # Add the filter name, which is unique to every module.
        return s.lower()
                    

    #x ?
    def human_path(self):
        '''Return the surrounding module and class name as a human string.
        
        Upper case is reduced to lower-case.
        
        This is not escaped enough for URL usage. Within a Django
        codebase adhering to Python code conventions, it is unique.
        It is usable where security is less important but human 
        readability and a lowercase appearence are prefered e.g. 
        filesystems.
        '''
        modstr = self.__module__
        
        # <last module> _ <classname>
        classpath = "{}_{}".format(
            modstr[modstr.rfind('.')+1:],
            type(self).__name__
        )

        return classpath.lower()

        
    def file_name(self, base_name, extension):
        '''
        Generate a filename from a base string.
        '''
        return base_name + '-' + self.id_str_short() + '.' + extension


    def save_info_callback(self, src_format):
        '''
        Gather and choose between configs about how to save filter results.
        Probes into several settings. If present, settings file wins, 
        filter config wins, discovered state. 
        @ifilter instance of a Filter
        '''
        # defaults
        iformat = src_format
        jpeg_quality = settings.jpeg_quality
        
        # Overrides of output format. Filter wins.
        if (settings.format_override):
            iformat = settings.format_override
        if hasattr(self, 'iformat') and self.iformat:
            iformat = self.iformat

        if iformat == 'jpeg':
            # Overrides of JPEG compression quality. Filter wins.
            if hasattr(self, 'jpeg_quality') and self.jpeg_quality:
                jpeg_quality = self.jpeg_quality
                
        return {'format': iformat, 'quality': jpeg_quality}
        
        
    def process(self, src_file):
        '''
        Wrap a Python file handle for processing a reform.
        Return should be a BytesIO buffer or similar. Some APIs do not
        include file saving, but most will deal with a generic Python
        buffer.
                 
        'save_info_callback' makes decisions about how the resulting 
        buffer should be saved. There is no need to call this function 
        for dev, but final versions should respect the environment by 
        calling it and acting on the results. Current implementation 
        needs the source format, then checks with overall and filter 
        settings, then returns decisions on 'format' and 'jpeg_quality'.
                
        @src_file an open Python file handle 
        @return a BytesIO or similar
        '''
        raise NotImplementedError
        

class PillowMixin:

    # def ensure_save(self, pillow):
        # if pillow.mode in ('RGBA', 'LA'):
            # background = Image.new(pillow.mode[:-1], pillow.size, self.fill_color)
            # background.paste(pillow, pillow.split()[-1])
            # image = background
            # im.convert("RGB")

            
    def process(self, src_file):
        src_image = PILImage.open(src_file)
        
        # write_attrs currently {format, jpeg_quality}
        write_attrs = self.save_info_callback(
                    FORMAT_PILLOW_APP[src_image.format],
                    )
        #! this wouldn't work for non-local files would it? AFAIK yes,
        # given storage backends
        # dst_fname = self.file_name(
                # Path(src_file.name).stem,
                # write_attrs['format']
            # )
            
        # mods on the save data
        # convert the returned format to PIL
        app_format = write_attrs['format']
        write_attrs['format'] = FORMAT_APP_PILLOW[write_attrs['format']]
        
        # Add some general write attributes. Pillow ignores the unusable.        
        write_attrs['progressive'] = True  
        write_attrs['optimize'] = True

        # break out processing, it's the only action that changes
        # across different filters
        pil_dst = self.pillow_actions(src_image) or src_image

        #! No transparency
        pil_dst = pil_dst.convert("RGB")
        write_attrs['quality'] = 85

        out_buff = BytesIO()

        pil_dst.save(
            out_buff,
            **write_attrs
        )
        
        return (out_buff, app_format)


    def pillow_actions(self, pillow):
        '''chain of actions to reform an instance of pillow.image.
        This section of the 
        '''
        raise NotImplementedError
        

class Format(PillowMixin, Filter):
    '''Establish the format for an image. 
    Set iformat=None means the image is unchanged.
    '''
    iformat=None
    jpeg_quality=None
    
    def __new__(cls, *args, **kwargs):
        #print('called Format new')
        check_image_formats(cls.__name__, 'iformat', cls.iformat)    
        check_jpeg_quality(cls.__name__, 'jpeg_quality', cls.jpeg_quality)       
        return super().__new__(cls, *args, **kwargs)

            
    def pillow_actions(self, pillow):
        # By passing this allows us to use the filter for format reform.
        return pillow
    
    
                        
class Resize(Format):
    '''Resize n image.
    Shrinks inside the box defined by the given args. So the result will
    usually be smaller width or height than the given box.
    A base class e.g.
        class Large(image.ResizeFilter):
            width=513
            height=760    
            iformat='png'
    '''
    width = None
    height = None
    
    
    def __new__(cls, *args, **kwargs):
        cls.testAttrNotFalse('width', 'height')
        return super().__new__(cls, *args, **kwargs)
        
    def pillow_actions(self, pillow):
        pillow = image_processes.resize_aspect(
            pillow, 
            self.width, 
            self.height
        )
        return pillow
        

        
                                    
class ResizeSmart(Format):
    '''Resize an image.
    This resize lays the image on a background of ''fill-color'.
    So the result always matches the given sizes.
    A base class e.g.
        class Large(image.ResizeFilter):
            width=513
            height=760    
            tpe='PNG'
    '''
    width = None
    height = None
    fill_color="white"
    
    
    def __new__(cls, *args, **kwargs):
        cls.testAttrNotFalse('width', 'height')
        return super().__new__(cls, *args, **kwargs)
        
    def pillow_actions(self, pillow):
        pillow = image_processes.resize_smart(
            pillow, 
            self.width, 
            self.height, 
            self.fill_color
        )
        return pillow

    
    
class Crop(Format):
    '''Resize and maybe re-format an image.
    A base class e.g.
        class Large(image.CropFilter):
            width=513
            height=760    
            tpe='PNG'
    '''
    width = None
    height = None
    
    def __new__(cls, *args, **kwargs):
        cls.testAttrNotFalse('width', 'height')
        return super().__new__(cls, *args, **kwargs)
        
    def pillow_actions(self, pillow):
        pillow = image_processes.crop(
            pillow, 
            self.width, 
            self.height
        )
        return pillow


class SmartCrop(Format):
    '''Resize and maybe re-format an image.
    A base class e.g.
        class Large(image.CropFilter):
            width=513
            height=760    
            tpe='PNG'
    '''
    width = None
    height = None
    fill_color="white"

    
    def __new__(cls, *args, **kwargs):
        cls.testAttrNotFalse('width', 'height')
        return super().__new__(cls, *args, **kwargs)
        
    def pillow_actions(self, pillow):
        pillow = image_processes.crop(
            pillow, 
            self.width, 
            self.height
        )
        return pillow


class Thumb(ResizeSmart):
    width=64
    height=64
    iformat='png'
