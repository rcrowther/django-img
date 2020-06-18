from image import filters_pillow, register, registry
from image import filters_wand



#@image.register
class Thumb(filters_pillow.ResizeSmart):
    width=64
    height=64
    format='png'



@register()
class Format(filters_wand.Format):
    jpeg_quality = 85
    pop = False
    greyscale=False
    cool= False
    warm = False
    strong = False
    film = False
    watermark = "image/watermark.png"
    
registry.register(Thumb)
