from PIL import Image as PILImage
import math



def resize_aspect(pillow, width, height):
    '''
    Resize if the image is too big, preserving aspect ratio.
    Will not resize if dimensions match or are less than the source.
    @return an image within the given dimensions. The image is usually 
    smaller in one dimension than the given space.
    '''
    b = pillow.getbbox()
    current_width = b[2] - b[0]
    current_height = b[3] - b[1]
        
    width_reduce = current_width - width
    height_reduce = current_height - height
  
    if (width_reduce > height_reduce and width_reduce > 0):
        h =  math.floor((width/current_width) * current_height)
        return pillow.resize((width, h))        
    elif (height_reduce > width_reduce and height_reduce > 0):
        w =  math.floor((height/current_height) * current_width)
        return pillow.resize((w, height))
    else:
        return pillow



def crop(pillow, width, height):
    '''
    Crop if image is too big.
    Crop is anchored at centre. 
    Will not crop if both dimensions match or are less than the source.
    @return an image within the given dimensions. The image may be 
    smaller in one dimension than the given space.
    '''
    b = pillow.getbbox()
    current_width = b[2] - b[0]
    current_height = b[3] - b[1]
    
    width_reduce = current_width - width
    height_reduce = current_height - height

    # Only crop if the image is too big
    if ((width_reduce > 0) or (height_reduce > 0)):
        x = 0
        y = 0
        if (width_reduce > 0):
            x = width_reduce >> 1
        if (height_reduce > 0):
            y = height_reduce >> 1
        # Crop!
        pillow = pillow.crop((x, y, x + width, y + height))
    return pillow



def fill(pillow, width, height, fill_color="white"):
    '''
    Fill round an image to a box.
    Image must be smaller than the giveen box. Checking is 
    regarded as a seperate operation.
    '''
    b = pillow.getbbox()
    current_width = b[2] - b[0]
    current_height = b[3] - b[1]
        
    # Palette images with Transparency expressed in bytes should be 
    # converted to RGBA images
    # Whatever that means.
    bg = PILImage.new('RGBA', (width, height), fill_color)

    x = (width - current_width) >> 1
    y = (height - current_height) >> 1

    bg.paste(pillow, (x, y))
    return bg



def crop_smart(pillow, width, height, fill_color="white"):
    '''Fit the given image to the given size.
    A general-purpose transformation.
    If the image is too large, it is shrunk to fit then, if necessary,
    filled to size.
    If too small, image is filled to size
    @return image of the given dimensions.
    '''
    rs = crop(pillow, width, height)
    f = fill(rs, width, height, fill_color)
    return f


    
def resize_smart(pillow, width, height, fill_color="white"):
    '''Resize to the given dimensions.
    If the image is too large, it is shrunk to fit then, if necessary,
    filled to size.
    If too small, image is filled to size
    @return image of the given dimensions.
    '''
    rs = resize_aspect(pillow, width, height)
    f = fill(rs, width, height, fill_color)
    return f



