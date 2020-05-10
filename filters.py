from image.utils import ModulePath
#x check_jpeg_quality
from image.settings import (
    settings, 
    check_jpeg_quality, 
    check_image_formats, 
    check_value_range, 
    check_positive,
    check_boolean,
    check_file,
)

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

    #! cached property?
    def path_str(self):
        '''
        Return the dotted module and classname as a string.
        
        Should be unique, and work as an id for the class. Moreover, it 
        should persist across code versions.
        
        Used for id purposes in the registry.
        '''
        return self.__module__ + '.' + type(self).__name__
    
        
    #! cached property?
    #! put the pk in?
    def id_str_short(self):
        '''
        Id for a filter, usable for keys.
        This is not guarenteed unique. it is to be concisely different 
        so avoid provoking storage backends, It depends on the 
        filter being placed in unique module packages. Which, in Django,
        they would be, inside app names.
        Currently formed as <module parent> + '_' + <filtername> 
        '''
        p = ModulePath.from_str(self.__module__)
        
        # protect against no module path, as generic 'app'
        md_str = 'app'

        # Take the second-last element. The leaf element in the 
        # surrounding system is always 'image_file', which is generic, 
        # but the parent element is distinctive, often an appname, so 
        # useful.                  
        if (p.size > 1):
            md_str = p.branch.leaf.str 
        
        # Add the filter name, which is unique to every module.
        return md_str + '_' + type(self).__name__.lower()
                    

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
        jpeg_quality = settings.reforms.jpeg_quality
        
        # Overrides of output format. Settings first...
        if (settings.reforms.format_override):
            iformat = settings.reforms.format_override

        #,,,but Filter wins.
        if hasattr(self, 'format') and self.format:
            iformat = self.format

        if iformat == 'jpg':
            # Overrides of JPEG compression quality. Filter wins.
            if hasattr(self, 'jpeg_quality') and self.jpeg_quality:
                jpeg_quality = self.jpeg_quality
                
        return {'format': iformat, 'jpeg_quality': jpeg_quality}
        
        
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
        
        
        
# Class code here on is mixins. They estabish attributes and checks, 
# skeletons to hang image-processing code on.

class FormatMixin():
    '''Establish the format for an image. 
    Set format=None means the image is unchanged.
    Most filters will contain and build from this base class.
    '''
    format=None
    jpeg_quality=None
    
    def __new__(cls, *args, **kwargs):
        check_image_formats(cls.__name__, 'format', cls.format)    
        check_jpeg_quality(cls.__name__, 'jpeg_quality', cls.jpeg_quality)  
        return super().__new__(cls, *args, **kwargs)



class PhotoFXMixin():
    '''Establish the format for an image. 
    Set format=None means the image is unchanged.
    Most filters will contain and build from this base class.
    '''
    pop=False
    greyscale=False    
    night=False
    warm=False
    strong=False
    film=False
    no=False
    watermark=''
    
    def __new__(cls, *args, **kwargs):
        check_boolean(cls.__name__, 'pop', cls.pop)    
        check_boolean(cls.__name__, 'greyscale', cls.greyscale)    
        check_boolean(cls.__name__, 'night', cls.night)    
        check_boolean(cls.__name__, 'warm', cls.warm)    
        check_boolean(cls.__name__, 'strong', cls.strong)    
        check_boolean(cls.__name__, 'film', cls.film)    
        check_boolean(cls.__name__, 'no', cls.no)    
        check_file(cls.__name__, 'watermark', cls.watermark)    
        return super().__new__(cls, *args, **kwargs)
                   
                   
                                
class ResizeCropMixin():
    '''Resize n image.
    Shrinks inside the box defined by the given args. So the result will
    usually be smaller width or height than the given box.
    A base class.
    '''
    width = None
    height = None
    
    def __new__(cls, *args, **kwargs):
        check_positive(cls.__name__, 'width', cls.width)
        check_positive(cls.__name__, 'height', cls.height)
        return super().__new__(cls, *args, **kwargs)
        
        
                                    
class ResizeCropSmartMixin(ResizeCropMixin):
    '''Resize an image.
    This resize lays the image on a background of ''fill-color'.
    So the result always matches the given sizes.
    A base class
    '''
    fill_color="white"
    
    
    def __new__(cls, *args, **kwargs):
        #? No test for color
        return super().__new__(cls, *args, **kwargs)

