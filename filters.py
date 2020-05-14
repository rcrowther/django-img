
from image.configuration_checks import (
    check_jpeg_quality, 
    check_image_formats, 
    check_value_range, 
    check_positive,
    check_boolean,
    check_file,
)

print('create filters')


class PlacementError(Exception):
    """
    Custom exception for attempted registration of Filters not in an 'image_filers' module
    """
    pass


        
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
      
    #? cache
    @classmethod
    def _module_path_human(cls):
        ''' 
        Human readable module path.
        Used to refer to a filter in the registry and templates. 
        Currently based on the module path and classname.
        '''
        mp = cls.__module__.split('.')
        
        # We encourage users to place filters in a 
        # module called image_filters'. This would involve a lot of
        # repetition in template code. So an 'image_filters' element is removed from the path.
        # That risks a collision with
        # filters placed in the root of an app, so insist on placement in 'image filters'.
        if (mp[-1] == 'image_filters'):
            del(mp[-1])
        else:
            raise PlacementError("Please locate Filters to be registered in an 'image filters' module: {}.{}".format(
                cls.__module__,
                cls.__name__
            ))        
        return mp
        
    @classmethod
    def human_id(cls):
        ''' 
        id for the filter.
        Used to refer in the registry and templates, so is human 
        readable. 
        Currently based on the module path and classname.
        '''
        p = cls._module_path_human()
        p.append( cls.__name__ )
        # That is unique, but we encourage users to place filters in a 
        # module called image_filters'. This would involve a lot of
        # repetition in template code. At the risk of a collision with
        # filters placed in the root of an app, we remove that part of 
        # the path.
        return ".".join(p)
        
    def filename(self, stem, extension):
        '''
        Generate a filename from a base string.
        An ammended filter path and name is appended to the stem,
        
        stem + '-' + ammended underscore path + '_' + filtername.lower() + '.' + extension
         
        It is to be concise, and near-unique to avoid provoking storage backends, 
        '''
        return "{}-{}_{}.{}".format(
            stem,
            "_".join(self._module_path_human()),
            type(self).__name__.lower(),
            extension
        )
        
        
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

