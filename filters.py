from image import image_processes
from image.constants import ALLOWED_EXTENSIONS
from io import BytesIO


class Filter():
    name = 'noName' # comes from classname?

    def path_str(self):
        '''
        Return thhe dotted module and classname as a string.
        
        Should be unique, and work as an id for the class. Moreover, it 
        should persist across code versions.
        '''
        return self.__module__ + '.' + type(self).__name__

    
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


    def process(self, pillow):
        '''chain of pillow actions to reform an instance of pillow.image'''
        raise NotImplementedError
        

    def run_to_buffer(self, pil_src, write_attrs):
        """
        Run a PIL src through the filter into a buffer.
        dest can be any file-like object
        write info is any extra params for PIL writing e.g. (jeeg/) quality optomise, etc. 
        return a bytebuffer containing the finished, written image.
        """
        pil_dst = self.process(pil_src) or pil_src

        out_buff = BytesIO()
        pil_dst.save(
            out_buff,
            **write_attrs
        )
        return out_buff
        
        
class FormatFilter(Filter):
    '''Establish the format for an image. Stting iformat=None means the image is unchanged.'''
    iformat = None
    
    def __new__(cls, *args, **kwargs):
        print('called FormatFilter')
        f = getattr(cls.iformat)
        if(f and (not(f in ALLOWED_EXTENSIONS))):
            raise ValueError("{} attribute format must be one of {}".format(
                cls.name, 
                "'" + "', '".join(ALLOWED_EXTENSIONS.append('None')) + "'")
            )            
        return super(Filter, cls).__new__(cls, *args, **kwargs)
    
    def process(self, pillow):
        # By passing this allows us to use the filter for format reform.
        return pillow
                        
                        
class ResizeFilter(FormatFilter):
    '''Resize n image.
    Shrinks inside the box defined by the given args. So the result will
    usually be smaller width or height than the given box.
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
        #print("called new")
        #print(str(dir(cls)))
        #print(str(args))
        nulled = [x for x in ['width', 'height', 'iformat',] if (not(getattr(cls, x)))]
        if (len(nulled) > 0):
            raise ValueError("{} attributes must be set. {} return None.".format(
                cls.name, 
                "'" + "', '".join(nulled) + "'")
            )
        return super(FormatFilter, cls).__new__(cls, *args, **kwargs)
        
    def process(self, pillow):
        pillow = image_processes.resize_aspect(
            pillow, 
            self.width, 
            self.height
        )
        return pillow
        
                                
class ResizeSmartFilter(FormatFilter):
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
        #print("called new")
        #print(str(dir(cls)))
        #print(str(args))
        nulled = [x for x in ['width', 'height', 'iformat', 'fill_color'] if (not(getattr(cls, x)))]
        if (len(nulled) > 0):
            raise ValueError("{} attributes must be set. {} return None.".format(
                cls.name, 
                "'" + "', '".join(nulled) + "'")
            )
        return super(FormatFilter, cls).__new__(cls, *args, **kwargs)
        
    def process(self, pillow):
        pillow = image_processes.resize_smart(
            pillow, 
            self.width, 
            self.height, 
            self.fill_color
        )
        return pillow


class CropFilter(FormatFilter):
    '''Resize and maybe re-format an image.
    A base class e.g.
        class Large(image.ResizeFilter):
            width=513
            height=760    
            tpe='PNG'
    '''
    width = None
    height = None
    
    def __new__(cls, *args, **kwargs):
        #print("called new")
        #print(str(dir(cls)))
        #print(str(args))
        nulled = [x for x in ['width', 'height', 'iformat'] if (not(getattr(cls, x)))]
        if (len(nulled) > 0):
            raise ValueError("{} attributes must be set. {} return None.".format(
                cls.name, 
                "'" + "', '".join(nulled) + "'")
            )
        return super(FormatFilter, cls).__new__(cls, *args, **kwargs)
        
    def process(self, pillow):
        pillow = image_processes.crop(
            pillow, 
            self.width, 
            self.height
        )
        return pillow
                    
# class Large(image.ResizeFilter):
    # width=513
    # height=760
    # iformat='jpg'


# class Medium(image.ResizeFilter):
    # width=630
    # height=272
    # iformat='jpg'

        
# class Small(image.ResizeFilter):
    # width=220
    # height=292
    # iformat='jpg'
        
# class Thumb(image.ResizeFilter):
    # width=98
    # height=64
    # iformat='png'

class Thumb(ResizeFilter):
    width=64
    height=64
    iformat='png'
