from PIL import Image as PILImage
from io import BytesIO
from image.filter_base import (
    FormatBase,
    ResizeBase,
    CropBase,
    ResizeSmartBase,
    CropSmartBase
)
from image import image_ops_pillow
from image.constants import FORMAT_APP_PILLOW, FORMAT_PILLOW_APP

print('create filters')




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

        # stash the returned app format
        app_format = write_attrs['format']

        # mods on the save data
        # convert the returned format to PIL
        write_attrs['format'] = FORMAT_APP_PILLOW[write_attrs['format']]
        
        # Add some general write attributes. Pillow ignores the unusable.        
        write_attrs['progressive'] = True  
        write_attrs['optimize'] = True

        # break out processing, it's the only action that changes
        # across different filters
        pil_dst = self.modify(src_image) or src_image

        #! No transparency
        pil_dst = pil_dst.convert("RGB")
        #! test. I think that;s the name.
        write_attrs['quality'] = 85

        out_buff = BytesIO()

        pil_dst.save(
            out_buff,
            **write_attrs
        )
        
        return (out_buff, app_format)

        


class Format(PillowMixin, FormatBase):
    '''Establish the format for an image. 
    Set iformat=None means the image is unchanged.
    '''
    
    
                        
class Resize(PillowMixin, ResizeBase, FormatBase):
    '''Resize n image.
    Shrinks inside the box defined by the given args. So the result will
    usually be smaller width or height than the given box.
    A base class e.g.
        class Large(image.Resize):
            width=513
            height=760    
            iformat='png'
    '''
    
    def modify(self, lib_image):
        lib_image = image_ops_pillow.resize_aspect(
            lib_image, 
            self.width, 
            self.height
        )
        return lib_image
        

class Crop(PillowMixin, CropBase, FormatBase):
    '''Resize and maybe re-format an image.
    A base class e.g.
        class Large(image.Crop):
            width=513
            height=760 
            tpe='png'
    '''
        
    def modify(self, lib_image):
        lib_image = image_ops_pillow.crop(
            lib_image,
            self.width,
            self.height
        )
        return lib_image
                
                                    
class ResizeSmart(PillowMixin, ResizeSmartBase, FormatBase):
    '''Resize an image.
    This resize lays the image on a background of ''fill-color'.
    So the result always matches the given sizes.
    A base class e.g.
        class Large(image.ResizeSmart):
            width=513
            height=760    
            tpe='png'
            fill_color="dark-green"
    '''
        
    def modify(self, lib_image):
        lib_image = image_ops_pillow.resize_smart(
            lib_image, 
            self.width, 
            self.height, 
            self.fill_color
        )
        return lib_image



class CropSmart(PillowMixin, CropSmartBase, FormatBase):
    '''Resize and maybe re-format an image.
    A base class e.g.
        class Large(image.CropSmart):
            width=513
            height=760    
            tpe='png'
            fill_color="coral"
    '''
        
    def modify(self, lib_image):
        lib_image = image_ops_pillow.crop_smart(
            lib_image, 
            self.width, 
            self.height
        )
        return lib_image



