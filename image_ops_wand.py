from wand.image import Image
from wand.color import Color
from wand.drawing import Drawing


def resize_aspect(wand, width, height):
    '''Resize if the image is too big.
    Preserves aspect ratio.
    Will not resize if dimensions match or are less than the source.
    @return an image within the given dimensions. The image is usually 
    smaller in one dimension than the given space.
    '''
    width_reduce = wand.width - width
    height_reduce = wand.height - height
  
    if (width_reduce > height_reduce and width_reduce > 0):
        h = round((width/wand.width) * wand.height)
        wand.resize(width, h)        
    elif (height_reduce > width_reduce and height_reduce > 0):
        w = round((height/wand.height) * wand.width)
        wand.resize(w, height)
    return wand
    
    
# http://docs.wand-py.org/en/0.5.9/index.html
# https://www.imagemagick.org/Usage/color_mods/#contrast-stretch    
def photoFX(wand, pop, grayscale, warm, night, strong, film, no, watermark):
    print('  photoFX op!')
    if (pop):
        wand.level(0.2, 0.9, gamma=1.1)

    # Reputedly fast and preserves transparency, but small erros 
    # will creep in, not a true greyscale but the visual effect.
    if (grayscale):
        print('  greyscale')
        matrix = [[0.333, 0.333, 0.333],
          [0.333, 0.333, 0.333],
          [0.333, 0.333, 0.333]]
        wand.color_matrix(matrix)
    if (night):
        print('cool')
        matrix = [[0.2, 0.0, 0],
           [0, 0.3, 0],
           [0, 0, 1]]
        wand.color_matrix(matrix)
    if (warm):
        print('warm')
        # matrix = [[1, 0, 0],
          # [0, 1, 0],
          # [0.5, 0, 0.5]]
        # wand.color_matrix(matrix)
        wand.modulate(brightness=100.0, saturation=100.0, hue=94.0)
    if (strong):
        wand.modulate(brightness=100.0, saturation=160.0, hue=100.0)
    if (no):
        insetX = wand.width >> 4
        insetY = wand.height >> 4
        insetX1 = wand.width - insetX
        insetY1 = wand.height - insetY
        with Drawing() as draw: 
            draw.stroke_color = Color('red')
            draw.stroke_width = 12
            draw.line((insetX, insetY1), (insetX1, insetY))
            draw.line((insetX, insetY), (insetX1, insetY1))        
            draw(wand)        

    if (film):
        print('  film')
        # frequency = 1
        # phase_shift = -180
        # amplitude = 0.02
        # bias = 0.8
        # wand.function('sinusoid', [frequency, phase_shift, amplitude, bias])
        # convert test.png  -fx '(1/(1+exp(10*(.5-u)))-0.006693)*1.013567' \
        #      sigmoidal.png
            #normalize()
        #resize(width=None, height=None,
        fx_filter="(hue > 0.6 || hue < 0.4) ? u : lightness"
        #fx_filter="u : lightness"
        #with wand as im:
        #with wand.fx(fx_filter) as im:
        #    wand = im
        wand = wand.fx(fx_filter)
        #wand.close()
        #wand = im 
            
    if (watermark):
        scale_width = wand.width >> 1
        
        with Image(filename=watermark) as overlay:
            # scale the overlay to the inset.            
            overlay.resize(scale_width, round(scale_width/overlay.width * overlay.height))
            wand.composite(
                overlay, 
                left=None, 
                top=None, 
                operator='dissolve', 
                arguments='35', 
                gravity='center'
            )
        
    #return wand


def crop(wand, width, height):
    '''
    Crop if image is too big.
    Crop is anchored at centre. 
    Will not crop if both dimensions match or are less than the source.
    @return an image within the given dimensions. The image may be 
    smaller in one dimension than the given space.
    '''
    current_width = wand.width
    current_height = wand.height
    
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
        wand.crop(left=x, top=y, width=width, height=height)
    return wand


def fill(wand, width, height, fill_color="white"):
    #https://stackoverflow.com/questions/1787356/use-imagemagick-to-place-an-image-inside-a-larger-canvas
    current_width = wand.width
    current_height = wand.height

    if ((width < current_width) or (height < current_height)):
        with Color(fill_color) as bg:
            wand.background_color = bg
            x = (width - current_width) >> 1
            y = (height - current_height) >> 1
            wand.extent(width=width, height=height, x=x, y=y)
  
  
def crop_smart(wand, width, height, fill_color="white"):
    '''Fit the given image to the given size.
    A general-purpose transformation.
    If the image is too large, it is shrunk to fit then, if necessary,
    filled to size.
    If too small, image is filled to size
    @return image of the given dimensions.
    '''
    crop(wand, width, height)
    fill(wand, width, height, fill_color)
    
    
def resize_smart(wand, width, height, fill_color="white"):
    '''Resize to the given dimensions.
    If the image is too large, it is shrunk to fit then, if necessary,
    filled to size.
    If too small, image is filled to size
    @return image of the given dimensions.
    '''
    resize_aspect(wand, width, height)
    fill(wand, width, height, fill_color)
