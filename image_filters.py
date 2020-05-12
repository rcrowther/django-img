from image import filters_pillow
from image import filters_wand, registry

#@image.register
class Thumb(filters_pillow.ResizeSmart):
    width=64
    height=64
    format='png'

# class Format(filters_wand.Format):
    # # black_level = 0.2
    # # white_level = 0.9
    # #format ='jpg'
    # jpeg_quality = 85
    # pop = False
    # greyscale=False
    # cool= False
    # warm = False
    # strong = False
    # film = False

registry.register(Thumb)
