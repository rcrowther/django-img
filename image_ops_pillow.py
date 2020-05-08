from PIL import Image as PILImage


def fill(pillow, width, height, fill_color="white"):
    '''
    Expand to the given size filling with the given color.
    If an image is too large for the given size, nothing happens. 
    The original is not changed, e.g. aspect ration is preserved.
    The given image must smaller, or the same size, in both dimnsions. 
    '''
    b = pillow.getbbox()
    current_width = b[2] - b[0]
    current_height = b[3] - b[1]

    if ((current_width >= width) and (current_height >= height)):
        return pillow
        
    # Palette images with Transparency expressed in bytes should be 
    # converted to RGBA images
    # Whatever that means.
    bg = PILImage.new('RGBA', (width, height), fill_color)

    x = (width - current_width) >> 1
    y = (height - current_height) >> 1

    bg.paste(pillow, (x, y))
    return bg


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
        x1 = current_width
        y = 0
        y1 = current_height
        if (width_reduce > 0):
            x = width_reduce >> 1
            x1 = x + width
        if (height_reduce > 0):
            y = height_reduce >> 1
            y1 = y + height
        # Crop!
        pillow = pillow.crop((x, y, x1, y1))
    return pillow


def resize_aspect(pillow, width, height):
    '''Resize if the image is too big.
    Preserves aspect ratio.
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
        # is 655 * 393 within 513*768  became 513*595
        h = round((width/current_width) * current_height)
        return pillow.resize((width, h))        
    elif (height_reduce > width_reduce and height_reduce > 0):
        w = round((height/current_height) * current_width)
        return pillow.resize((w, height))
    else:
        return pillow


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



