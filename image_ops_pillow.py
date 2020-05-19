from PIL import Image as PILImage
import math



def resize_aspect(pillow, width, height):
    '''
    Resize if the image is too big, preserving aspect ratio.
    Will not resize if dimensions match or are less than the source.
    @return an image within the given dimensions. The image is usually 
    smaller in one dimension than the given space.
    '''
    s = pillow.size
    current_width = s[0]
    current_height = s[1]
    width_reduce = current_width - width
    height_reduce = current_height - height
    if (width_reduce > height_reduce and width_reduce > 0):
        h =  math.floor((width * current_height)/current_width)
        return pillow.resize((width, h))        
    elif (height_reduce > width_reduce and height_reduce > 0):
        w =  math.floor((height * current_width)/current_height)
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
    s = pillow.size
    current_width = s[0]
    current_height = s[1]
    
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
    # NB: This converts to RGB. Not an issue, as fill runs last.
    s = pillow.size
    current_width = s[0]
    current_height = s[1]

    x = (width - current_width) >> 1
    #x = math.floor((width - current_width) / 2)
    y = (height - current_height) >> 1
        
    # needed for the split
    pillow.load() 
    bg = PILImage.new('RGB', (width, height), fill_color)

    # paste down, mask from the alpha channel (usually last)
    bg.paste(pillow, (x, y),  mask=pillow.split()[-1])
    
    return bg




