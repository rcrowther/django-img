from wand.image import Image
from io import BytesIO
from image.filters import (
    Filter,
    FormatMixin,
    PhotoFXMixin,
    ResizeCropMixin,
    ResizeCropSmartMixin,
)
from image import image_ops_wand
from image.constants import FORMAT_APP_PILLOW, FORMAT_PILLOW_APP



class WandProcess():
    '''
    Not: Imagemagik/Wand modifies in place, so there is no need for 
    returns from on modify() or image_ops.
    '''
    def process(self, src_file):
        image = Image(file=src_file)
 
        # write_attrs currently {format, jpeg_quality}
        write_attrs = self.save_info_callback(
                    FORMAT_PILLOW_APP[image.format],
                    )
 
        # break out processing, it's the only action that changes
        # across different filters
        self.modify(image) or image
        
        # set the format
        image.format = FORMAT_APP_PILLOW[write_attrs['format']]
        
        # set JPEG quality?
        image.compression_quality = write_attrs['jpeg_quality']
        
        #! No transparency
        #pil_dst = pil_dst.convert("RGB")
        #write_attrs['quality'] = 85

        out_buff = BytesIO()
        print(str(image.format))

        image.save(
            out_buff,
        )
        
        return (out_buff,  write_attrs['format'])

    def modify(self, lib_image):
        # '''
        # Modify the image.
        # 'process hadles the image load and save. 'process' calls this 
        # method to transform the image. Basely this is the only method
        # that needs to be changed, even for a filter that performs a 
        # new kind of transformation (no need to change the load and save 
        # in 'process).
        # The method should usually call super() to enable builtin code.
        
        # @lib_image the class used by the library to wrap image data
        # @return the same kind of class
        # '''
        #raise NotImplementedError
        pass


#class Format(WandProcess, PhotoFXBase, FormatBase):
class Format(PhotoFXMixin, FormatMixin, WandProcess, Filter):
    '''Establish the format for an image. 
    Set iformat=None means the image is unchanged.
    '''

    def modify(self, lib_image):
        super().modify(lib_image)
        image_ops_wand.photoFX(
            lib_image, 
            self.pop, 
            self.greyscale, 
            self.warm, 
            self.night, 
            self.strong, 
            self.film,
            self.no,
            self.watermark,
        )
    

# class Format(WandProcess, FormatBase):
    # '''Establish the format for an image. 
    # Set iformat=None means the image is unchanged.
    # '''
    
    
                        
class Resize(ResizeCropMixin,  Format):
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
        image_ops_wand.resize_aspect(
            lib_image,
            self.width,
            self.height
            )
        super().modify(lib_image)

        
class Crop(ResizeCropMixin, Format):
    '''Resize and maybe re-format an image.
    A base class e.g.
        class Large(image.Crop):
            width=513
            height=760    
            tpe='png'
    '''
        
    def modify(self, lib_image):
        image_ops_wand.crop(
            lib_image,
            self.width,
            self.height
        )
        super().modify(lib_image)



class ResizeSmart(ResizeCropSmartMixin, Format):
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
        print('wand resizesmart')
        image_ops_wand.resize_smart(
            lib_image, 
            self.width, 
            self.height, 
            self.fill_color
        )
        super().modify(lib_image)



class CropSmart(ResizeCropSmartMixin, Format):
    '''Resize and maybe re-format an image.
    A base class e.g.
        class Large(image.CropSmart):
            width=513
            height=760    
            tpe='png'
            fill_color="coral"
    '''
        
    def modify(self, lib_image):
        image_ops_wand.crop_smart(
            lib_image, 
            self.width, 
            self.height
        )
        super().modify(lib_image)
        
